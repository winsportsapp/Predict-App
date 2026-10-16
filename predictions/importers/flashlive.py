"""FlashLive Sports API (RapidAPI): Flashscore's data, including its team and
player names, so imported names match the Team rows entered by hand.

https://rapidapi.com/tipsters/api/flashlive-sports

Quota: the free RapidAPI plan allows only a small number of requests a month.
One request returns a whole day of one sport, so which matches are imported
(FLASHLIVE_TOURNAMENTS / FLASHLIVE_TEAMS / FLASHLIVE_EXCLUDE_TOURNAMENTS) does
not change the number of requests.
"""

import logging
import re
import time
from fnmatch import fnmatchcase
from datetime import datetime, timedelta, timezone as dt_timezone

import requests
from django.conf import settings

from predictions.constants import DEFAULT_FOOTBALL_SECOND_DIV_EXCLUDES
from .base import (
    REQUEST_TIMEOUT,
    ExternalEvent,
    H2HSummary,
    Provider,
    ProviderError,
    ProviderQuotaExceededError,
    make_session,
    match_score,
    resolve_side,
)

logger = logging.getLogger(__name__)

API_HOST = "flashlive-sports.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}/v1"
LOCALE = "en_INT"

# Our Sport.name -> FlashLive sport_id. Only these sports are imported, and
# each one costs API quota on every run. Add or override a sport with FLASHLIVE_SPORT_IDS;
# check IDs with `python manage.py sync_external_matches --list-sports`.
DEFAULT_SPORT_IDS = {
    "Football": 1,
    "Tennis": 2,
    "Cricket": 13,
    "Badminton": 21,
    "Hockey": 24,
}



def _parse_rapidapi_reset(headers, default_date_str="October 25 at 03:05 PM IST"):
    # Check headers (case-insensitive) for reset seconds
    reset_val = None
    if isinstance(headers, (dict, requests.structures.CaseInsensitiveDict)):
        for k, v in headers.items():
            if str(k).lower() in ("x-ratelimit-requests-reset", "ratelimit-reset"):
                reset_val = v
                break
    reset_dt = None
    if reset_val:
        try:
            secs = int(reset_val)
            reset_dt = datetime.now(dt_timezone.utc) + timedelta(seconds=secs)
            ist_dt = reset_dt.astimezone(dt_timezone(timedelta(hours=5, minutes=30)))
            return ist_dt.strftime("%B %d at %I:%M %p IST"), reset_dt
        except Exception:
            pass
    return default_date_str, reset_dt


def _format_rapidapi_reset(headers, default_date_str="October 25 at 03:05 PM IST"):
    date_str, _ = _parse_rapidapi_reset(headers, default_date_str)
    return date_str


import sys

# default throttle delay (can be set to 0 in tests)
DEFAULT_THROTTLE_DELAY = 0 if "test" in sys.argv else 1.2

# In-memory quota exhaustion cache: {key_name: reset_datetime}
_KEY_QUOTA_STATUS = {
    "primary": None,
    "secondary": None,
}


def reset_flashlive_quota_status():
    _KEY_QUOTA_STATUS["primary"] = None
    _KEY_QUOTA_STATUS["secondary"] = None


# FlashLive's list endpoint only reaches 7 days either side of today.
MAX_INDENT_DAYS = 7

CALLED_OFF_STAGES = {"POSTPONED", "CANCELED", "CANCELLED", "ABANDONED"}

# Auto-expansion of series/tier names to constituent tournaments so an admin
# can simply enter "*Super 1000*" or "*Grand Slam*" without needing to type every open.
BWF_TIER_EXPANSIONS = {
    "super 1000": {
        "*all england*",
        "*china open*",
        "*indonesia open*",
        "*malaysia open*",
        "*super 1000*",
    },
    "super 750": {
        "*denmark open*",
        "*india open*",
        "*french open*",
        "*singapore open*",
        "*japan open*",
        "*china masters*",
        "*super 750*",
    },
    "super 500": {
        "*malaysia masters*",
        "*indonesia masters*",
        "*thailand open*",
        "*hong kong open*",
        "*arctic open*",
        "*korea open*",
        "*kumamoto masters*",
        "*australian open*",
        "*canada open*",
        "*super 500*",
    },
}

TENNIS_TIER_EXPANSIONS = {
    "grand slam": {
        "*wimbledon*",
        "*us open*",
        "*french open*",
        "*australian open*",
        "*grand slam*",
    },
}

FOOTBALL_TIER_EXPANSIONS = {
    "world: uefa champions league": {"europe: champions league", "*champions league*"},
    "uefa champions league": {"europe: champions league", "*champions league*"},
    "champions league": {"europe: champions league", "*champions league*"},
    "ucl": {"europe: champions league", "*champions league*"},
    "premier league": {"england: premier league"},
    "epl": {"england: premier league"},
    "la liga": {"spain: laliga", "*laliga*"},
    "laliga": {"spain: laliga", "*laliga*"},
    "serie a": {"italy: serie a"},
    "bundesliga": {"germany: bundesliga"},
    "ligue 1": {"france: ligue 1"},
    "isl": {"india: isl*", "india: indian super league*"},
}


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
        stats_api_key=None,
        stats_session=None,
        throttle_delay=None,
    ):
        self.api_key = api_key if api_key is not None else getattr(settings, "RAPIDAPI_KEY", "")
        self.stats_api_key = (
            stats_api_key
            if stats_api_key is not None
            else (getattr(settings, "RAPIDAPI_STATS_KEY", "") if api_key is None else "")
        )
        self.throttle_delay = (
            DEFAULT_THROTTLE_DELAY if throttle_delay is None else throttle_delay
        )
        self._use_global_quota = (session is None and stats_session is None)
        self._instance_quota_status = {"primary": None, "secondary": None}
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
        self.session = session or (
            make_session({"x-rapidapi-key": self.api_key, "x-rapidapi-host": API_HOST})
            if self.api_key
            else None
        )
        # Dedicated session for H2H and recent form requests using secondary key
        self.stats_session = stats_session or (
            make_session({"x-rapidapi-key": self.stats_api_key, "x-rapidapi-host": API_HOST})
            if self.stats_api_key
            else self.session
        )
        if self.session is None and self.stats_session is not None:
            self.session = self.stats_session
        # Requests made by this instance, reported by the command so usage
        # against the monthly quota can be followed in the logs.
        self.requests_made = 0
        self.stats_requests_made = 0

    # -- Provider interface ------------------------------------------------

    def supports(self, sport_name):
        return sport_name in self.sport_ids

    def fetch_fixtures(self, sport_name, days_ahead, new_day_only=False, with_odds=False):
        teams = self.teams.get(sport_name.lower(), set())

        active_tournaments = set(self.tournaments)
        active_exclude_tournaments = set(self.exclude_tournaments)
        try:
            from predictions.models import Sport

            sport_obj = Sport.objects.filter(name__iexact=sport_name).first()
            if sport_obj:
                db_inc = _patterns(sport_obj.tournaments_filter)
                if db_inc:
                    active_tournaments = db_inc
                db_exc = _patterns(sport_obj.exclude_tournaments_filter)
                if db_exc:
                    active_exclude_tournaments = db_exc | set(self.exclude_tournaments)
        except Exception:
            pass

        # Auto-expand tier aliases (e.g. Badminton Super 1000/750/500, Tennis Grand Slam)
        sport_key = str(sport_name).strip().lower()
        if sport_key == "badminton" and active_tournaments:
            expanded = set(active_tournaments)
            for pat in active_tournaments:
                for tier_key, opens in BWF_TIER_EXPANSIONS.items():
                    if tier_key in pat:
                        expanded.update(opens)
            active_tournaments = expanded
        elif sport_key == "tennis" and active_tournaments:
            expanded = set(active_tournaments)
            for pat in active_tournaments:
                for tier_key, opens in TENNIS_TIER_EXPANSIONS.items():
                    if tier_key in pat:
                        expanded.update(opens)
            active_tournaments = expanded
        elif sport_key == "football":
            active_exclude_tournaments = set(active_exclude_tournaments) | DEFAULT_FOOTBALL_SECOND_DIV_EXCLUDES
            if active_tournaments:
                expanded = set()
                for pat in active_tournaments:
                    p_lower = pat.lower().strip()
                    if p_lower in FOOTBALL_TIER_EXPANSIONS:
                        expanded.update(FOOTBALL_TIER_EXPANSIONS[p_lower])
                    else:
                        expanded.add(pat)
                active_tournaments = expanded

        if not (active_tournaments or teams):
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
                if _matches_any(keys, active_exclude_tournaments):
                    continue
                whole_tournament = _matches_inclusion(keys, active_tournaments)
                for raw in group.get("EVENTS") or []:
                    if not whole_tournament and not _plays(raw, teams):
                        continue
                    home_name = str(raw.get("HOME_NAME") or "").strip().lower()
                    away_name = str(raw.get("AWAY_NAME") or "").strip().lower()
                    if _matches_any([home_name, away_name], active_exclude_tournaments):
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
        except ProviderQuotaExceededError:
            raise
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
        except ProviderQuotaExceededError:
            raise
        except ProviderError:
            try:
                data = self._get("/events/live-odds", {"event_id": external_id, "locale": LOCALE})
            except ProviderQuotaExceededError:
                raise
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

    def fetch_h2h_and_form(self, match):
        """Fetch H2H history and recent 5-match form using FlashLive's /events/h2h endpoint.
        Uses stats_session (RAPIDAPI_STATS_KEY) to isolate quota from fixture sync.
        """
        ext_id = getattr(match, "external_id", "")
        if not ext_id:
            return None

        data = self._get_stats("/events/h2h", {"event_id": ext_id, "locale": LOCALE})
        if not data:
            return None

        groups = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if "GROUPS" in item:
                        groups.extend(item.get("GROUPS") or [])
                    else:
                        groups.append(item)
        elif isinstance(data, dict):
            groups = data.get("GROUPS") or [data]

        h2h_events = []
        team_a_events = []
        team_b_events = []

        team_a_lower = match.team_a.name.lower()
        team_b_lower = match.team_b.name.lower()

        for g in groups:
            if not isinstance(g, dict):
                continue
            label = str(g.get("GROUP_LABEL") or g.get("NAME") or "")
            label_lower = label.lower()
            evs = g.get("ITEMS") or g.get("EVENTS") or []
            if "head-to-head" in label_lower or "h2h" in label_lower:
                h2h_events.extend(evs)
                continue

            side = resolve_side(match.team_a.name, match.team_b.name, label)
            if side == "A":
                team_a_events.extend(evs)
            elif side == "B":
                team_b_events.extend(evs)
            elif not team_a_events and "last matches" in label_lower:
                team_a_events.extend(evs)
            elif not team_b_events and "last matches" in label_lower:
                team_b_events.extend(evs)

        past_matches = []
        team_a_wins = 0
        team_b_wins = 0
        draws = 0

        for raw in h2h_events[:10]:
            if not isinstance(raw, dict):
                continue
            home_raw = raw.get("HOME_PARTICIPANT_NAME_ONE") or raw.get("HOME_PARTICIPANT") or raw.get("HOME_NAME") or ""
            away_raw = raw.get("AWAY_PARTICIPANT_NAME_ONE") or raw.get("AWAY_PARTICIPANT") or raw.get("AWAY_NAME") or ""
            home = str(home_raw).lstrip("*").strip()
            away = str(away_raw).lstrip("*").strip()
            if not home and not away:
                continue

            hs = raw.get("HOME_SCORE_FULL") if raw.get("HOME_SCORE_FULL") is not None else raw.get("HOME_SCORE_CURRENT")
            aws = raw.get("AWAY_SCORE_FULL") if raw.get("AWAY_SCORE_FULL") is not None else raw.get("AWAY_SCORE_CURRENT")

            start = raw.get("START_TIME") or raw.get("START_UTIME")
            date_str = ""
            if start:
                try:
                    date_str = datetime.fromtimestamp(int(start), tz=dt_timezone.utc).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    pass

            winner_outcome = _determine_flashlive_winner(raw, hs, aws)
            side_home = resolve_side(match.team_a.name, match.team_b.name, home)
            side_away = resolve_side(match.team_a.name, match.team_b.name, away)
            if side_home == "A" or side_away == "B":
                is_team_a_home = True
            elif side_home == "B" or side_away == "A":
                is_team_a_home = False
            else:
                is_team_a_home = team_a_lower in home.lower()

            if winner_outcome == "HOME":
                winner_name = home
                winner_side = "A" if is_team_a_home else "B"
                if winner_side == "A":
                    team_a_wins += 1
                else:
                    team_b_wins += 1
            elif winner_outcome == "AWAY":
                winner_name = away
                winner_side = "B" if is_team_a_home else "A"
                if winner_side == "B":
                    team_b_wins += 1
                else:
                    team_a_wins += 1
            else:
                winner_name = "Draw"
                winner_side = "D"
                draws += 1

            score_str = str(raw.get("CURRENT_RESULT") or "").strip()
            if not score_str and (hs is not None and aws is not None):
                score_str = f"{hs} - {aws}"
            elif score_str and ":" in score_str:
                score_str = score_str.replace(":", " - ")

            past_matches.append({
                "date": date_str,
                "competition": raw.get("EVENT_NAME") or raw.get("TOURNAMENT_NAME") or raw.get("SHORT_NAME") or match.sport.name,
                "home": home,
                "away": away,
                "score": score_str,
                "winner": winner_name,
                "winner_side": winner_side,
            })

        team_a_form = _parse_flashlive_recent_form(team_a_events[:5], match.team_a.name)
        team_b_form = _parse_flashlive_recent_form(team_b_events[:5], match.team_b.name)

        return H2HSummary(
            team_a_wins=team_a_wins,
            team_b_wins=team_b_wins,
            draws=draws,
            total_matches=len(past_matches),
            past_matches=past_matches,
            team_a_form=team_a_form,
            team_b_form=team_b_form,
        )

    # -- helpers -----------------------------------------------------------

    def _get_quota_reset(self, key_name):
        if self._use_global_quota:
            return _KEY_QUOTA_STATUS.get(key_name)
        return self._instance_quota_status.get(key_name)

    def _set_quota_reset(self, key_name, reset_dt):
        if self._use_global_quota:
            _KEY_QUOTA_STATUS[key_name] = reset_dt
        else:
            self._instance_quota_status[key_name] = reset_dt

    def _execute_http(self, session, key_name, path, params):
        if key_name == "primary":
            self.requests_made += 1
        else:
            self.stats_requests_made += 1

        if self.throttle_delay > 0:
            time.sleep(self.throttle_delay)  # Polite throttle to prevent RapidAPI per-second burst rate limits
        try:
            resp = session.get(BASE_URL + path, params=params, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            err_str = str(exc).lower()
            if "too many 429" in err_str or "quota" in err_str:
                default_date = "October 25 at 03:05 PM IST" if key_name == "primary" else "November 13 at 08:00 PM IST"
                self._set_quota_reset(key_name, datetime.now(dt_timezone.utc) + timedelta(hours=12))
                raise ProviderQuotaExceededError(
                    f"FlashLive {key_name} key quota reached (429). Quota restores around {default_date}."
                ) from exc
            raise ProviderError(f"FlashLive request failed ({key_name} key): {exc}") from exc

        if resp.status_code == 404:
            return []

        if resp.status_code == 429:
            msg = resp.text[:200]
            default_date = "October 25 at 03:05 PM IST" if key_name == "primary" else "November 13 at 08:00 PM IST"
            reset_str, reset_dt = _parse_rapidapi_reset(resp.headers, default_date)
            self._set_quota_reset(key_name, reset_dt or (datetime.now(dt_timezone.utc) + timedelta(hours=12)))
            label = "Primary" if key_name == "primary" else "Secondary"
            raise ProviderQuotaExceededError(
                f"FlashLive {label} API monthly quota on RapidAPI reached (500 requests/month). Quota restores on {reset_str}."
            )

        if resp.status_code != 200:
            raise ProviderError(
                f"FlashLive {path} returned HTTP {resp.status_code} ({key_name} key): {resp.text[:200]}"
            )

        try:
            return resp.json().get("DATA") or []
        except ValueError as exc:
            raise ProviderError(f"FlashLive {path} returned invalid JSON ({key_name} key)") from exc

    def _execute_with_failover(self, preferred_name, fallback_name, preferred_session, fallback_session, path, params):
        pref_key_str = self.api_key if preferred_name == "primary" else self.stats_api_key
        fallback_key_str = self.stats_api_key if fallback_name == "secondary" else self.api_key

        if not self.api_key and not self.stats_api_key:
            raise ProviderError("Neither RAPIDAPI_KEY nor RAPIDAPI_STATS_KEY is set.")

        has_fallback = (
            fallback_session is not None
            and fallback_session != preferred_session
            and bool(fallback_key_str)
            and fallback_key_str != pref_key_str
        )

        now = datetime.now(dt_timezone.utc)
        pref_reset = self._get_quota_reset(preferred_name)
        fb_reset = self._get_quota_reset(fallback_name)

        # If preferred key has no credentials but fallback does, route directly to fallback
        if not pref_key_str and has_fallback:
            return self._execute_http(fallback_session, fallback_name, path, params)

        # 1. If preferred key is known to be quota-exhausted and fallback is active and not exhausted,
        # route straight to fallback directly!
        if pref_reset and now < pref_reset and has_fallback and (not fb_reset or now >= fb_reset):
            logger.info(
                "FlashLive %s key is known to be exhausted until %s; using %s key directly for %s",
                preferred_name, pref_reset, fallback_name, path
            )
            return self._execute_http(fallback_session, fallback_name, path, params)

        # 2. Try preferred key
        try:
            return self._execute_http(preferred_session, preferred_name, path, params)
        except ProviderQuotaExceededError as pref_err:
            if not has_fallback:
                raise pref_err

            # Check if fallback key is also known to be exhausted
            if fb_reset and now < fb_reset:
                raise ProviderQuotaExceededError(
                    f"FlashLive monthly quota reached on all available keys (Primary & Secondary exhausted)."
                ) from pref_err

            logger.warning(
                "FlashLive %s key reached quota (%s); failing over to %s key for %s",
                preferred_name, pref_err, fallback_name, path
            )
            try:
                return self._execute_http(fallback_session, fallback_name, path, params)
            except ProviderQuotaExceededError as fb_err:
                raise ProviderQuotaExceededError(
                    f"FlashLive monthly quota reached on all available keys (Primary & Secondary exhausted)."
                ) from fb_err

    def _get(self, path, params):
        return self._execute_with_failover(
            preferred_name="primary",
            fallback_name="secondary",
            preferred_session=self.session,
            fallback_session=self.stats_session,
            path=path,
            params=params,
        )

    def _get_stats(self, path, params):
        if not self.stats_api_key and not self.api_key:
            return []
        primary_session = self.session if self.api_key else None
        secondary_session = self.stats_session if self.stats_api_key else None
        preferred_session = secondary_session or primary_session
        fallback_session = primary_session if secondary_session and primary_session != secondary_session else None
        return self._execute_with_failover(
            preferred_name="secondary" if secondary_session else "primary",
            fallback_name="primary",
            preferred_session=preferred_session,
            fallback_session=fallback_session,
            path=path,
            params=params,
        )

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
    if not values:
        return set()
    if isinstance(values, str):
        values = [
            p.strip().strip('"\'')
            for p in values.replace("\r\n", "\n").replace("\n", ",").split(",")
            if p.strip().strip('"\'')
        ]
    return {
        str(v).strip().strip('"\'').lower()
        for v in values
        if str(v).strip().strip('"\'')
    }


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
    """True if any key equals a pattern, fits one with "*" wildcards,
    or contains the pattern as a substring if no wildcards were specified."""
    for key in keys:
        for pat in patterns:
            p = str(pat).strip().lower()
            if not p:
                continue
            if fnmatchcase(key, p):
                return True
            if "*" not in p and "?" not in p and p in key:
                return True
    return False


def _matches_inclusion(keys, patterns):
    """True if any key matches an inclusion pattern, respecting word/delimiter boundaries."""
    for key in keys:
        for pat in patterns:
            p = str(pat).strip().lower()
            if not p:
                continue
            if fnmatchcase(key, p):
                return True
            if "*" not in p and "?" not in p:
                if p == key:
                    return True
                if re.search(rf"(?:^|:\s*){re.escape(p)}(?:\s*\(|\s*$)", key, re.IGNORECASE):
                    return True
    return False


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


def _determine_flashlive_winner(raw, hs, aws):
    """Determine outcome ('HOME', 'AWAY', or 'DRAW') from FlashLive raw match dict."""
    home_p = str(raw.get("HOME_PARTICIPANT") or "")
    away_p = str(raw.get("AWAY_PARTICIPANT") or "")
    if home_p.startswith("*"):
        return "HOME"
    if away_p.startswith("*"):
        return "AWAY"

    winner_code = str(raw.get("WINNER") or "").strip()
    if winner_code == "1":
        return "HOME"
    elif winner_code == "2":
        return "AWAY"

    tm = str(raw.get("TEAM_MARK") or "").strip().lower()
    wis = str(raw.get("WIS") or "").strip().lower()
    hr = str(raw.get("H_RESULT") or "").strip().upper()
    if tm in ("home", "away"):
        if wis == "w" or hr == "WIN":
            return "HOME" if tm == "home" else "AWAY"
        elif wis == "l" or hr == "LOST":
            return "AWAY" if tm == "home" else "HOME"
        elif wis == "d" or hr == "DRAW":
            return "DRAW"

    if hs is not None and aws is not None:
        try:
            h_int = int(str(hs).split("/")[0].strip())
            a_int = int(str(aws).split("/")[0].strip())
            if h_int > a_int:
                return "HOME"
            elif a_int > h_int:
                return "AWAY"
            elif h_int == a_int:
                return "DRAW"
        except (ValueError, TypeError):
            pass

    return "DRAW"


def _parse_flashlive_recent_form(raw_events, team_name):
    form_list = []
    for ev in raw_events:
        if not isinstance(ev, dict):
            continue
        home_raw = ev.get("HOME_PARTICIPANT_NAME_ONE") or ev.get("HOME_PARTICIPANT") or ev.get("HOME_NAME") or ""
        away_raw = ev.get("AWAY_PARTICIPANT_NAME_ONE") or ev.get("AWAY_PARTICIPANT") or ev.get("AWAY_NAME") or ""
        home = str(home_raw).lstrip("*").strip()
        away = str(away_raw).lstrip("*").strip()
        if not home and not away:
            continue

        hs = ev.get("HOME_SCORE_FULL") if ev.get("HOME_SCORE_FULL") is not None else ev.get("HOME_SCORE_CURRENT")
        aws = ev.get("AWAY_SCORE_FULL") if ev.get("AWAY_SCORE_FULL") is not None else ev.get("AWAY_SCORE_CURRENT")

        start = ev.get("START_TIME") or ev.get("START_UTIME")
        date_str = ""
        if start:
            try:
                date_str = datetime.fromtimestamp(int(start), tz=dt_timezone.utc).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass

        tm = str(ev.get("TEAM_MARK") or "").strip().lower()
        if tm == "home":
            is_home = True
            opponent = away
        elif tm == "away":
            is_home = False
            opponent = home
        else:
            s_home = match_score(team_name, home)
            s_away = match_score(team_name, away)
            is_home = (s_home >= s_away)
            opponent = away if is_home else home

        wis = str(ev.get("WIS") or "").strip().lower()
        hr = str(ev.get("H_RESULT") or "").strip().upper()
        if wis == "w" or hr == "WIN":
            res = "W"
        elif wis == "l" or hr == "LOST":
            res = "L"
        elif wis == "d" or hr == "DRAW":
            res = "D"
        else:
            winner_outcome = _determine_flashlive_winner(ev, hs, aws)
            if winner_outcome == "HOME":
                res = "W" if is_home else "L"
            elif winner_outcome == "AWAY":
                res = "L" if is_home else "W"
            else:
                res = "D"

        score_str = str(ev.get("CURRENT_RESULT") or "").strip()
        if not score_str and (hs is not None and aws is not None):
            score_str = f"{hs} - {aws}"
        elif score_str and ":" in score_str:
            score_str = score_str.replace(":", " - ")

        form_list.append({
            "date": date_str,
            "opponent": opponent,
            "score": score_str,
            "result": res,
            "competition": ev.get("EVENT_NAME") or ev.get("TOURNAMENT_NAME") or ev.get("SHORT_NAME") or "",
        })
    return form_list


