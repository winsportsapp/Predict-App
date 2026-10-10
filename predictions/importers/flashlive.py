"""FlashLive Sports API (RapidAPI): Flashscore's data, including its team and
player names, so imported names match the Team rows entered by hand.

https://rapidapi.com/tipsters/api/flashlive-sports

Quota: the free RapidAPI plan allows only a small number of requests a month.
One request returns a whole day of one sport, so which matches are imported
(FLASHLIVE_TOURNAMENTS / FLASHLIVE_TEAMS / FLASHLIVE_EXCLUDE_TOURNAMENTS) does
not change the number of requests.
"""

import logging
from fnmatch import fnmatchcase
from datetime import datetime, timedelta, timezone as dt_timezone

import requests
from django.conf import settings

from .base import REQUEST_TIMEOUT, ExternalEvent, Provider, ProviderError, make_session

logger = logging.getLogger(__name__)

API_HOST = "flashlive-sports.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}/v1"
LOCALE = "en_INT"

# Our Sport.name -> FlashLive sport_id. Only these sports are imported, and
# each one costs API quota on every run. Hockey (field hockey) is left out
# on purpose: it is entered by hand. Add a sport with FLASHLIVE_SPORT_IDS
# (field hockey is 24); check the IDs with
# `python manage.py sync_external_matches --list-sports`.
DEFAULT_SPORT_IDS = {
    "Football": 1,
    "Tennis": 2,
    "Cricket": 13,
    "Badminton": 21,
}

# FlashLive's list endpoint only reaches 7 days either side of today.
MAX_INDENT_DAYS = 7

CALLED_OFF_STAGES = {"POSTPONED", "CANCELED", "CANCELLED", "ABANDONED"}


class FlashLiveProvider(Provider):
    name = "flashlive"

    def __init__(
        self,
        api_key=None,
        tournaments=None,
        sport_ids=None,
        session=None,
        teams=None,
        exclude_tournaments=None,
        utc_offset=None,
    ):
        self.api_key = api_key if api_key is not None else settings.RAPIDAPI_KEY
        # Tournament names or IDs; "*" wildcards allowed, e.g. "* ATP*".
        self.tournaments = _patterns(
            tournaments if tournaments is not None else settings.FLASHLIVE_TOURNAMENTS
        )
        self.exclude_tournaments = _patterns(
            exclude_tournaments
            if exclude_tournaments is not None
            else settings.FLASHLIVE_EXCLUDE_TOURNAMENTS
        )
        # "Sport:Team" entries: import any match of that team, whatever the
        # tournament (e.g. every "Cricket:India" international).
        self.teams = {}
        for entry in teams if teams is not None else settings.FLASHLIVE_TEAMS:
            sport, sep, team = str(entry).partition(":")
            if sep and team.strip():
                self.teams.setdefault(sport.strip().lower(), set()).add(
                    team.strip().lower()
                )
        self.sport_ids = {
            **DEFAULT_SPORT_IDS,
            **{
                name: int(value)
                for name, value in (
                    sport_ids
                    if sport_ids is not None
                    else settings.FLASHLIVE_SPORT_IDS
                ).items()
            },
        }
        # Whole hours from UTC that FlashLive's days are counted in (it
        # rejects 5.5). With 5, "tomorrow" runs 00:30 to 00:30 IST instead
        # of UTC's 05:30 to 05:30.
        self.utc_offset = int(
            utc_offset if utc_offset is not None else settings.FLASHLIVE_UTC_OFFSET
        )
        self.local_tz = dt_timezone(timedelta(hours=self.utc_offset))
        self.session = session or make_session(
            {"x-rapidapi-key": self.api_key, "x-rapidapi-host": API_HOST}
        )
        # Requests made by this instance, reported by the command so usage
        # against the monthly quota can be followed in the logs.
        self.requests_made = 0

    # -- Provider interface ------------------------------------------------

    def supports(self, sport_name):
        return sport_name in self.sport_ids

    def fetch_fixtures(self, sport_name, days_ahead, new_day_only=False, with_odds=False):
        teams = self.teams.get(sport_name.lower(), set())
        if not (self.tournaments or teams):
            # Without a filter this would import every match in the world.
            return []
        last_day = min(days_ahead, MAX_INDENT_DAYS)
        # new_day_only: just the day entering the window (1 request). Earlier
        # days were imported by previous daily runs.
        days = [last_day] if new_day_only else range(0, last_day + 1)
        events = []
        for day in days:
            odds_map = self.fetch_odds(sport_name, day) if with_odds else {}
            for group in self._list_events(sport_name, day):
                keys = _tournament_keys(group)
                if _matches_any(keys, self.exclude_tournaments):
                    continue
                whole_tournament = _matches_any(keys, self.tournaments)
                for raw in group.get("EVENTS") or []:
                    if not whole_tournament and not _plays(raw, teams):
                        continue
                    event = self._to_event(sport_name, group, raw)
                    if event:
                        if event.external_id in odds_map:
                            h, a, d = odds_map[event.external_id]
                            if h is not None:
                                event.home_odds = h
                            if a is not None:
                                event.away_odds = a
                            if d is not None:
                                event.draw_odds = d
                        events.append(event)
        return events

    def fetch_odds(self, sport_name, indent_days=0):
        """{external_id: (home_odds, away_odds, draw_odds)} for events on indent_days.
        1 request per sport per day."""
        if sport_name not in self.sport_ids:
            return {}
        try:
            data = self._get(
                "/events/list-main-odds",
                {
                    "sport_id": self.sport_ids[sport_name],
                    "indent_days": indent_days,
                    "locale": LOCALE,
                    "timezone": self.utc_offset,
                },
            )
        except ProviderError as exc:
            logger.debug(
                "FlashLive list-main-odds not available for %s day %s: %s",
                sport_name,
                indent_days,
                exc,
            )
            return {}

        results = {}
        events_list = []
        if isinstance(data, dict):
            events_list = data.get("events") or data.get("EVENTS") or []
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if "EVENTS" in item:
                        events_list.extend(item.get("EVENTS") or [])
                    elif "events" in item:
                        events_list.extend(item.get("events") or [])
                    else:
                        events_list.append(item)

        for event in events_list:
            if not isinstance(event, dict):
                continue
            eid = event.get("EVENT_ID") or event.get("event_id") or event.get("ID")
            if not eid:
                continue
            odds_obj = event.get("ODDS") or event.get("odds") or event
            home, away, draw = _extract_odds_tuple(odds_obj)
            if home is not None or away is not None or draw is not None:
                results[str(eid)] = (home, away, draw)
        return results

    def fetch_event_odds(self, external_id):
        """(home_odds, away_odds, draw_odds) for a single event ID, or None."""
        try:
            data = self._get("/events/odds", {"event_id": external_id, "locale": LOCALE})
        except ProviderError:
            try:
                data = self._get("/events/live-odds", {"event_id": external_id, "locale": LOCALE})
            except ProviderError:
                return None

        if isinstance(data, list):
            for bet in data:
                if not isinstance(bet, dict):
                    continue
                bet_type = str(bet.get("BETTING_TYPE") or "").upper()
                if "1X2" in bet_type or "HOME/AWAY" in bet_type:
                    for period in bet.get("PERIODS") or []:
                        obn = str(period.get("OBN") or "").upper()
                        stage = str(period.get("ODDS_STAGE") or "").upper()
                        if "FULL_TIME" in obn or "*MATCH" in stage or "*FULL TIME" in stage:
                            for group in period.get("GROUPS") or []:
                                for market in group.get("MARKETS") or []:
                                    home, away, draw = _extract_odds_tuple(market)
                                    if home is not None or away is not None:
                                        return home, away, draw

        if isinstance(data, dict):
            odds_obj = data.get("ODDS") or data.get("odds") or data
            home, away, draw = _extract_odds_tuple(odds_obj)
            if home is not None or away is not None or draw is not None:
                return home, away, draw
        return None

    def fetch_matches_odds(self, matches):
        """Given an iterable of Match objects, return {match.pk: (home, away, draw)}.

        Optimized for API quota: groups matches by (sport_name, day) and uses
        bulk /events/list-main-odds (1 request per sport per day) rather than
        making 1 individual request per match. Falls back to fetch_event_odds
        only for events not found in the bulk day map.
        """
        results = {}
        today = datetime.now(self.local_tz).date()

        by_day = {}
        for m in matches:
            ext_id = getattr(m, "external_id", "")
            if not ext_id or not getattr(m, "sport", None):
                continue
            sport_name = m.sport.name
            if not self.supports(sport_name):
                continue
            start = m.start_time
            indent = (
                (start.astimezone(self.local_tz).date() - today).days
                if start
                else -999
            )
            by_day.setdefault((sport_name, indent), []).append(m)

        for (sport_name, indent_days), match_list in by_day.items():
            if 0 <= indent_days <= MAX_INDENT_DAYS:
                bulk_map = self.fetch_odds(sport_name, indent_days)
                for m in match_list:
                    if m.external_id in bulk_map:
                        results[m.pk] = bulk_map[m.external_id]

            for m in match_list:
                if m.pk not in results:
                    odds = self.fetch_event_odds(m.external_id)
                    if odds and (
                        odds[0] is not None or odds[1] is not None or odds[2] is not None
                    ):
                        results[m.pk] = odds

        return results

    def fetch_results(self, sport_name, kickoffs):
        # One request per kickoff day covers every match that day, so only
        # the days pending matches were played on are fetched.
        today = datetime.now(self.local_tz).date()
        days = sorted({
            (start.astimezone(self.local_tz).date() - today).days
            for start in kickoffs.values()
        })
        found = {}
        for day in days:
            if not -MAX_INDENT_DAYS <= day <= 0:
                continue
            for group in self._list_events(sport_name, day):
                for raw in group.get("EVENTS") or []:
                    if str(raw.get("EVENT_ID")) in kickoffs:
                        event = self._to_event(sport_name, group, raw)
                        if event:
                            found[event.external_id] = event
        return found

    def list_tournaments(self, sport_name, day=0):
        """[(full name, match count), ...] for one day, e.g.
        ("England: Premier League", 10). 1 request."""
        return sorted(
            (group.get("NAME") or "", len(group.get("EVENTS") or []))
            for group in self._list_events(sport_name, day)
        )

    def list_sports(self):
        """[(id, name), ...] as FlashLive numbers its sports."""
        data = self._get("/sports/list", {})
        return [(item.get("ID"), item.get("NAME")) for item in data or []]

    # -- helpers -----------------------------------------------------------

    def _get(self, path, params):
        if not self.api_key:
            raise ProviderError("RAPIDAPI_KEY is not set.")
        self.requests_made += 1
        try:
            response = self.session.get(
                BASE_URL + path, params=params, timeout=REQUEST_TIMEOUT
            )
        except requests.RequestException as exc:
            raise ProviderError(f"FlashLive request failed: {exc}") from exc
        if response.status_code == 404:
            # FlashLive answers 404 for a day with no events.
            return []
        if response.status_code != 200:
            raise ProviderError(
                f"FlashLive {path} returned HTTP {response.status_code}: "
                f"{response.text[:200]}"
            )
        try:
            return response.json().get("DATA") or []
        except ValueError as exc:
            raise ProviderError(f"FlashLive {path} returned invalid JSON") from exc

    def _list_events(self, sport_name, indent_days):
        return self._get(
            "/events/list",
            {
                "sport_id": self.sport_ids[sport_name],
                "indent_days": indent_days,
                "locale": LOCALE,
                "timezone": self.utc_offset,
            },
        )

    def _to_event(self, sport_name, group, raw):
        event_id = raw.get("EVENT_ID")
        home, away = raw.get("HOME_NAME"), raw.get("AWAY_NAME")
        start = raw.get("START_TIME") or raw.get("START_UTIME")
        if not (event_id and home and away and start):
            logger.warning("Skipping incomplete FlashLive event: %r", event_id)
            return None

        stage = str(raw.get("STAGE") or "").upper()
        called_off = stage in CALLED_OFF_STAGES
        finished = str(raw.get("STAGE_TYPE") or "").upper() == "FINISHED"

        home_score = ""
        away_score = ""
        if finished and not called_off:
            if sport_name in ("Tennis", "Badminton"):
                h_sets, a_sets = _count_sets(raw)
                if h_sets > 0 or a_sets > 0:
                    home_score = str(h_sets)
                    away_score = str(a_sets)
            if not home_score and not away_score:
                hs = raw.get("HOME_SCORE_CURRENT")
                aws = raw.get("AWAY_SCORE_CURRENT")
                if hs is not None:
                    home_score = str(hs).strip()
                if aws is not None:
                    away_score = str(aws).strip()

        odds_obj = raw.get("ODDS") or raw.get("odds")
        home_odds, away_odds, draw_odds = (
            _extract_odds_tuple(odds_obj) if odds_obj else (None, None, None)
        )

        return ExternalEvent(
            source=self.name,
            external_id=str(event_id),
            sport=sport_name,
            event_name=_event_name(group),
            home=home.strip(),
            away=away.strip(),
            start_time=datetime.fromtimestamp(int(start), tz=dt_timezone.utc),
            result=(
                _result(sport_name, raw) if finished and not called_off else None
            ),
            called_off=called_off,
            home_image=_first(raw.get("HOME_IMAGES")),
            away_image=_first(raw.get("AWAY_IMAGES")),
            home_score=home_score,
            away_score=away_score,
            home_odds=home_odds,
            away_odds=away_odds,
            draw_odds=draw_odds,
        )


def _patterns(values):
    return {str(v).strip().lower() for v in values if str(v).strip()}


def _tournament_keys(group):
    """The names/IDs a tournament can be listed by: an ID, the full name
    ("England: Premier League", the precise choice) or the short name
    ("Premier League", which may also match another country's league)."""
    keys = (
        group.get("TOURNAMENT_TEMPLATE_ID"),
        group.get("TOURNAMENT_STAGE_ID"),
        group.get("TOURNAMENT_ID"),
        group.get("NAME"),
        group.get("SHORT_NAME"),
        _event_name(group),
    )
    return [str(k).strip().lower() for k in keys if k]


def _matches_any(keys, patterns):
    """True if any key equals a pattern, or fits one with "*" wildcards."""
    return any(fnmatchcase(key, pattern) for key in keys for pattern in patterns)


def _plays(raw, teams):
    """True if one of `teams` (lower-case names) plays in this event."""
    return bool(teams) and any(
        str(raw.get(side) or "").strip().lower() in teams
        for side in ("HOME_NAME", "AWAY_NAME")
    )


def _event_name(group):
    name = group.get("SHORT_NAME") or group.get("NAME") or ""
    # "ENGLAND: Premier League" -> "Premier League"
    return name.split(": ", 1)[-1].strip()[:150]


def _first(images):
    if isinstance(images, list) and images:
        return str(images[0])
    return ""


def _count_sets(raw):
    """Count sets won by home and away from HOME_SCORE_PART_X / AWAY_SCORE_PART_X."""
    home_sets, away_sets = 0, 0
    for i in range(1, 6):
        hp = raw.get(f"HOME_SCORE_PART_{i}")
        ap = raw.get(f"AWAY_SCORE_PART_{i}")
        if hp is not None and ap is not None:
            try:
                hp_val, ap_val = int(hp), int(ap)
                if hp_val > ap_val:
                    home_sets += 1
                elif ap_val > hp_val:
                    away_sets += 1
            except (TypeError, ValueError):
                pass
    return home_sets, away_sets


RETIREMENT_KEYWORDS = ("RETIRED", "RET.", "WALKOVER", "W.O.")


def _result(sport_name, raw):
    """'home', 'away', 'draw' or None for a finished event."""
    from ..constants import DRAW_SPORTS

    stage = str(raw.get("STAGE") or "").upper()
    is_retired = any(kw in stage for kw in RETIREMENT_KEYWORDS)

    winner = str(raw.get("WINNER", "")).strip().lower()
    if winner in ("1", "home"):
        return "home"
    if winner in ("2", "away"):
        return "away"

    # If a player retired or walked over and FlashLive did not provide an explicit
    # WINNER, do NOT guess from partial sets/games (the retiring player may have won set 1).
    if is_retired:
        return None

    # A cricket score ("245/6") says nothing reliable about the winner or a
    # draw, so leave it for the admin to enter by hand.
    if sport_name == "Cricket":
        return None

    # For set-based sports (Tennis, Badminton), check individual set/game scores (PART_1 .. PART_5)
    if sport_name in ("Tennis", "Badminton"):
        home_sets, away_sets = _count_sets(raw)
        if home_sets > away_sets:
            return "home"
        if away_sets > home_sets:
            return "away"

    try:
        home = int(raw.get("HOME_SCORE_CURRENT"))
        away = int(raw.get("AWAY_SCORE_CURRENT"))
    except (TypeError, ValueError):
        return None
    if home > away:
        return "home"
    if away > home:
        return "away"

    # Only sports that permit a draw can return 'draw'
    if sport_name in DRAW_SPORTS:
        return "draw"

    return None


def _safe_float(v):
    try:
        if v is None:
            return None
        val = float(str(v).strip())
        return round(val, 2) if val > 0 else None
    except (ValueError, TypeError):
        return None


def _extract_odds_tuple(odds_obj):
    """Given an odds object/dict/list, returns (home_odds, away_odds, draw_odds)."""
    if odds_obj is None:
        return None, None, None

    # Handle FlashLive list of cell objects: [{'ODD_CELL_FIRST': ...}, ...]
    if isinstance(odds_obj, list):
        cells = {}
        for item in odds_obj:
            if isinstance(item, dict):
                for k, v in item.items():
                    if k.startswith("ODD_CELL_"):
                        val = v.get("VALUE") if isinstance(v, dict) else v
                        cells[k] = _safe_float(val)
        if cells:
            first = cells.get("ODD_CELL_FIRST")
            second = cells.get("ODD_CELL_SECOND")
            third = cells.get("ODD_CELL_THIRD")
            # 3-way market (Football: 1=First, X=Second, 2=Third)
            if first is not None and second is not None and third is not None:
                return first, third, second
            # 2-way market (Tennis/Cricket/Badminton: 1=Second, 2=Third)
            if second is not None and third is not None:
                return second, third, None
            if first is not None and second is not None:
                return first, second, None
            if first is not None and third is not None:
                return first, third, None

        # Check for legacy list format: [{'choice': '1', 'value': ...}, ...]
        home, draw, away = None, None, None
        has_legacy = False
        for item in odds_obj:
            if isinstance(item, dict):
                c = str(
                    item.get("choice") or item.get("type") or item.get("name") or ""
                ).upper()
                v = _safe_float(item.get("value") or item.get("odd") or item.get("odds"))
                if c in ("1", "HOME"):
                    home = v
                    has_legacy = True
                elif c in ("X", "DRAW"):
                    draw = v
                    has_legacy = True
                elif c in ("2", "AWAY"):
                    away = v
                    has_legacy = True
        if has_legacy:
            return home, away, draw
        return None, None, None

    if not isinstance(odds_obj, dict):
        return None, None, None

    # Check if odds_obj has ODD_CELL_* directly (e.g. market dict from /events/odds)
    first = odds_obj.get("ODD_CELL_FIRST")
    second = odds_obj.get("ODD_CELL_SECOND")
    third = odds_obj.get("ODD_CELL_THIRD")
    if first is not None or second is not None or third is not None:
        c1 = _safe_float(first.get("VALUE") if isinstance(first, dict) else first)
        c2 = _safe_float(second.get("VALUE") if isinstance(second, dict) else second)
        c3 = _safe_float(third.get("VALUE") if isinstance(third, dict) else third)
        if c1 is not None and c2 is not None and c3 is not None:
            return c1, c3, c2
        if c2 is not None and c3 is not None:
            return c2, c3, None
        if c1 is not None and c2 is not None:
            return c1, c2, None
        if c1 is not None and c3 is not None:
            return c1, c3, None

    # If odds_obj has an inner ODDS list/dict
    if "ODDS" in odds_obj or "odds" in odds_obj:
        inner = odds_obj.get("ODDS") or odds_obj.get("odds")
        if inner and inner is not odds_obj:
            res = _extract_odds_tuple(inner)
            if res != (None, None, None):
                return res

    main = odds_obj.get("main") or odds_obj.get("MAIN") or odds_obj
    if isinstance(main, list):
        return _extract_odds_tuple(main)

    if isinstance(main, dict):
        home = _safe_float(
            main.get("home")
            or main.get("HOME")
            or main.get("1")
            or odds_obj.get("HOME_ODD")
            or odds_obj.get("ODD_1")
        )
        draw = _safe_float(
            main.get("draw")
            or main.get("DRAW")
            or main.get("X")
            or odds_obj.get("DRAW_ODD")
            or odds_obj.get("ODD_X")
        )
        away = _safe_float(
            main.get("away")
            or main.get("AWAY")
            or main.get("2")
            or odds_obj.get("AWAY_ODD")
            or odds_obj.get("ODD_2")
        )
        return home, away, draw

    return None, None, None

