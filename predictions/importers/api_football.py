"""API-Football (API-Sports / RapidAPI) provider for Football.

https://api-sports.io / https://v3.football.api-sports.io

Free quota: 100 requests per day (resetting at 00:00 UTC) = ~3,000 req/month.
Provides fixtures, bookmaker odds, head-to-head (H2H), and recent form for Football.
"""

import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from fnmatch import fnmatchcase
import requests
from django.conf import settings

from .base import (
    REQUEST_TIMEOUT,
    ExternalEvent,
    H2HSummary,
    Provider,
    ProviderError,
    make_session,
    match_score,
    resolve_side,
)

logger = logging.getLogger(__name__)

DEFAULT_HOST = "v3.football.api-sports.io"
CALLED_OFF_STATUSES = {"PST", "CANC", "ABD", "SUSP", "INT", "WO"}
FINISHED_STATUSES = {"FT", "AET", "PEN"}
MAX_FREE_DAYS_AHEAD = 1


def _patterns(values):
    return {str(v).strip().lower() for v in values if str(v).strip()}


def _is_plan_limit_error(exc):
    msg = str(exc).lower()
    return "plan" in msg or "free plan" in msg or "access to this date" in msg


class APIFootballProvider(Provider):
    name = "api-football"

    def __init__(
        self,
        api_key=None,
        host=None,
        session=None,
        leagues=None,
        utc_offset=None,
        max_days_ahead=None,
        tournaments=None,
        exclude_tournaments=None,
    ):
        self.api_key = (
            api_key if api_key is not None else getattr(settings, "API_FOOTBALL_KEY", "")
        )
        self.host = (
            host if host is not None else getattr(settings, "API_FOOTBALL_HOST", DEFAULT_HOST)
        )
        self.leagues = (
            leagues if leagues is not None else getattr(settings, "API_FOOTBALL_LEAGUES", [])
        )
        # Whole hours from UTC that "today"/"tomorrow" are counted in.
        # Shared with FlashLive (settings.FLASHLIVE_UTC_OFFSET, default 5 for IST).
        self.utc_offset = int(
            utc_offset
            if utc_offset is not None
            else getattr(settings, "FLASHLIVE_UTC_OFFSET", 5)
        )
        self.local_tz = dt_timezone(timedelta(hours=self.utc_offset))

        # Max fixture lookahead window. Default 1 for Free plans (today + 1 day).
        self.max_days_ahead = int(
            max_days_ahead
            if max_days_ahead is not None
            else getattr(settings, "API_FOOTBALL_DAYS_AHEAD", MAX_FREE_DAYS_AHEAD)
        )

        self.tournaments = _patterns(
            tournaments
            if tournaments is not None
            else getattr(settings, "API_FOOTBALL_TOURNAMENTS", [])
        )
        self.exclude_tournaments = _patterns(
            exclude_tournaments
            if exclude_tournaments is not None
            else getattr(settings, "API_FOOTBALL_EXCLUDE_TOURNAMENTS", [])
        )
        self.requests_made = 0

        headers = {}
        if "rapidapi.com" in self.host.lower():
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.host,
            }
        else:
            headers = {
                "x-apisports-key": self.api_key,
            }

        self.session = session or make_session(headers)
        self.base_url = f"https://{self.host}"

    def supports(self, sport_name):
        return str(sport_name).strip().lower() == "football"

    def _tournament_matches(self, event_name, league_name):
        keys = [str(league_name).strip().lower(), str(event_name).strip().lower()]
        if self.exclude_tournaments:
            if any(fnmatchcase(k, pat) for k in keys for pat in self.exclude_tournaments):
                return False
        if self.tournaments:
            return any(fnmatchcase(k, pat) for k in keys for pat in self.tournaments)
        return True

    # -- Core endpoints ----------------------------------------------------

    def _get(self, path, params=None):
        if not self.api_key:
            raise ProviderError("API_FOOTBALL_KEY is not configured.")
        self.requests_made += 1
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise ProviderError(f"API-Football request failed: {exc}") from exc

        if resp.status_code != 200:
            raise ProviderError(
                f"API-Football {path} returned HTTP {resp.status_code}: {resp.text[:200]}"
            )

        try:
            payload = resp.json()
        except ValueError as exc:
            raise ProviderError(f"API-Football {path} returned invalid JSON") from exc

        errors = payload.get("errors")
        if errors:
            if isinstance(errors, dict) and any(errors.values()):
                raise ProviderError(f"API-Football error: {errors}")
            elif isinstance(errors, list) and errors:
                raise ProviderError(f"API-Football error: {errors}")

        return payload.get("response") or []

    # -- Fixtures & Odds ---------------------------------------------------

    def fetch_fixtures(self, sport_name, days_ahead, new_day_only=False, with_odds=False):
        if not self.supports(sport_name):
            return []

        today = datetime.now(self.local_tz).date()
        effective_max = max(0, self.max_days_ahead)
        days = (
            [min(days_ahead, effective_max)]
            if new_day_only
            else range(0, min(days_ahead, effective_max) + 1)
        )

        all_events = []
        for d in days:
            target_date = (today + timedelta(days=d)).isoformat()
            odds_map = self.fetch_odds(sport_name, indent_days=d) if with_odds else {}

            params = {"date": target_date}
            # If specific leagues are configured, query them; otherwise query all for the date
            raw_fixtures = []
            if self.leagues:
                for league_id in self.leagues:
                    try:
                        fixtures = self._get(
                            "/fixtures", {"date": target_date, "league": league_id}
                        )
                        raw_fixtures.extend(fixtures)
                    except ProviderError as exc:
                        if _is_plan_limit_error(exc):
                            logger.info(
                                "API-Football plan date limit reached for league %s on %s: %s",
                                league_id,
                                target_date,
                                exc,
                            )
                            break
                        logger.warning("Failed fetching league %s on %s: %s", league_id, target_date, exc)
            else:
                try:
                    raw_fixtures = self._get("/fixtures", params)
                except ProviderError as exc:
                    if _is_plan_limit_error(exc):
                        logger.info(
                            "API-Football plan date limit reached on %s: %s. Returning retrieved fixtures.",
                            target_date,
                            exc,
                        )
                        break
                    raise

            for item in raw_fixtures:
                league_obj = item.get("league", {})
                league_name = league_obj.get("name") or "Football"
                country = league_obj.get("country")
                event_name = f"{country}: {league_name}" if country else league_name

                if not self._tournament_matches(event_name, league_name):
                    continue

                event = self._to_event(item)
                if event:
                    if event.external_id in odds_map:
                        h, a, d = odds_map[event.external_id]
                        if h is not None:
                            event.home_odds = h
                        if a is not None:
                            event.away_odds = a
                        if d is not None:
                            event.draw_odds = d
                    all_events.append(event)

        return all_events

    def fetch_odds(self, sport_name, indent_days=0):
        """{external_id: (home_odds, away_odds, draw_odds)} for fixtures on target date."""
        if not self.supports(sport_name):
            return {}

        effective_max = max(0, self.max_days_ahead)
        if indent_days > effective_max:
            return {}

        today = datetime.now(self.local_tz).date()
        target_date = (today + timedelta(days=indent_days)).isoformat()
        try:
            data = self._get("/odds", {"date": target_date})
        except ProviderError as exc:
            logger.debug("API-Football /odds failed for %s: %s", target_date, exc)
            return {}

        results = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            fid = item.get("fixture", {}).get("id")
            if not fid:
                continue
            odds_tuple = _extract_api_football_odds(item.get("bookmakers") or [])
            if any(v is not None for v in odds_tuple):
                results[str(fid)] = odds_tuple

        return results

    def fetch_event_odds(self, external_id):
        """(home, away, draw) for a single fixture ID."""
        try:
            data = self._get("/odds", {"fixture": external_id})
        except ProviderError:
            return None

        if data and isinstance(data, list):
            item = data[0]
            odds_tuple = _extract_api_football_odds(item.get("bookmakers") or [])
            if any(v is not None for v in odds_tuple):
                return odds_tuple
        return None

    def fetch_results(self, sport_name, kickoffs):
        """{external_id: ExternalEvent} for finished/updated matches."""
        if not self.supports(sport_name):
            return {}

        found = {}
        # Fetch fixtures by ID
        for ext_id in kickoffs.keys():
            try:
                data = self._get("/fixtures", {"id": ext_id})
                if data and isinstance(data, list):
                    event = self._to_event(data[0])
                    if event:
                        found[event.external_id] = event
            except ProviderError as exc:
                logger.debug("Failed fetching result for fixture %s: %s", ext_id, exc)

        return found

    # -- Head-to-Head & Recent Form ----------------------------------------

    def fetch_h2h_and_form(self, match):
        """Fetch H2H history and recent 5-match form for both teams."""
        if not self.supports(match.sport.name):
            return None

        home_id, away_id = None, None

        # 1. Try finding team IDs from match.external_id
        if match.external_id:
            try:
                data = self._get("/fixtures", {"id": match.external_id})
                if data and isinstance(data, list):
                    fx = data[0].get("teams", {})
                    home_id = fx.get("home", {}).get("id")
                    away_id = fx.get("away", {}).get("id")
            except ProviderError:
                pass

        # 2. Fall back to team name search if team IDs unknown
        if not home_id:
            home_id = self._search_team_id(match.team_a.name)
        if not away_id:
            away_id = self._search_team_id(match.team_b.name)

        if not (home_id and away_id):
            logger.debug(
                "Could not resolve API-Football team IDs for %s vs %s",
                match.team_a.name,
                match.team_b.name,
            )
            return None

        # 3. Fetch H2H encounters (do NOT pass 'last' param as API-Football free plans reject it)
        past_matches = []
        team_a_wins = 0
        team_b_wins = 0
        draws = 0

        try:
            h2h_raw = self._get("/fixtures/headtohead", {"h2h": f"{home_id}-{away_id}"})
            if isinstance(h2h_raw, list):
                # Sort newest first and take the last 10 clashes
                h2h_raw.sort(key=lambda x: x.get("fixture", {}).get("date", ""), reverse=True)
                for item in h2h_raw[:10]:
                    parsed = _parse_h2h_encounter(item, match.team_a.name, match.team_b.name)
                    if parsed:
                        past_matches.append(parsed)
                        res = parsed.get("winner_side")
                        if res == "A":
                            team_a_wins += 1
                        elif res == "B":
                            team_b_wins += 1
                        elif res == "D":
                            draws += 1
        except ProviderError as exc:
            logger.warning("Failed fetching H2H for %s vs %s: %s", match.team_a, match.team_b, exc)

        # 4. Fetch recent form (last 5 matches for Team A & Team B)
        team_a_form = self._fetch_team_recent_form(home_id, match.team_a.name)
        team_b_form = self._fetch_team_recent_form(away_id, match.team_b.name)

        # If team form is not available from API (free plan restriction), fall back to H2H recent form
        if not team_a_form and past_matches:
            for p in past_matches[:5]:
                team_a_form.append({
                    "result": "W" if p.get("winner_side") == "A" else ("D" if p.get("winner_side") == "D" else "L"),
                    "opponent": match.team_b.name,
                    "score": p.get("score", ""),
                    "date": p.get("date", ""),
                })
        if not team_b_form and past_matches:
            for p in past_matches[:5]:
                team_b_form.append({
                    "result": "W" if p.get("winner_side") == "B" else ("D" if p.get("winner_side") == "D" else "L"),
                    "opponent": match.team_a.name,
                    "score": p.get("score", ""),
                    "date": p.get("date", ""),
                })

        return H2HSummary(
            team_a_wins=team_a_wins,
            team_b_wins=team_b_wins,
            draws=draws,
            total_matches=len(past_matches),
            past_matches=past_matches,
            team_a_form=team_a_form,
            team_b_form=team_b_form,
        )

    def _search_team_id(self, team_name):
        if not team_name:
            return None
        # 1. Exact name match
        try:
            data = self._get("/teams", {"name": team_name})
            if data and isinstance(data, list):
                return data[0].get("team", {}).get("id")
        except ProviderError:
            pass

        # 2. General search query
        try:
            data = self._get("/teams", {"search": team_name})
            if data and isinstance(data, list):
                return data[0].get("team", {}).get("id")
        except ProviderError:
            pass

        # 3. Clean common club suffixes/prefixes (FC, CF, SC, AFC, Club)
        import re
        cleaned = re.sub(r"\b(fc|cf|sc|afc|club)\b", "", team_name, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned and cleaned.lower() != team_name.lower():
            try:
                data = self._get("/teams", {"name": cleaned})
                if data and isinstance(data, list):
                    return data[0].get("team", {}).get("id")
                data = self._get("/teams", {"search": cleaned})
                if data and isinstance(data, list):
                    return data[0].get("team", {}).get("id")
            except ProviderError:
                pass

        return None

    def _fetch_team_recent_form(self, team_id, team_name):
        try:
            current_year = datetime.now().year
            fixtures = self._get("/fixtures", {"team": team_id, "season": current_year})
            finished = [
                f for f in fixtures
                if f.get("fixture", {}).get("status", {}).get("short") in FINISHED_STATUSES
            ]
            finished.sort(key=lambda x: x.get("fixture", {}).get("date", ""), reverse=True)
            results = []
            for item in finished[:5]:
                parsed = _parse_form_fixture(item, team_name)
                if parsed:
                    results.append(parsed)
            return results
        except ProviderError as exc:
            logger.debug("Failed fetching recent form for team %s: %s", team_id, exc)
            return []

    # -- Internal helpers --------------------------------------------------

    def _to_event(self, item):
        fixture = item.get("fixture", {})
        fid = fixture.get("id")
        date_str = fixture.get("date")
        if not (fid and date_str):
            return None

        teams = item.get("teams", {})
        home = teams.get("home", {}).get("name")
        away = teams.get("away", {}).get("name")
        if not (home and away):
            return None

        league = item.get("league", {})
        league_name = league.get("name") or "Football"
        country = league.get("country")
        event_name = f"{country}: {league_name}" if country else league_name

        status_code = fixture.get("status", {}).get("short") or ""
        called_off = status_code in CALLED_OFF_STATUSES
        finished = status_code in FINISHED_STATUSES

        goals = item.get("goals", {})
        hg = goals.get("home")
        ag = goals.get("away")
        home_score = str(hg) if hg is not None and finished else ""
        away_score = str(ag) if ag is not None and finished else ""

        result = None
        if finished and not called_off and hg is not None and ag is not None:
            if hg > ag:
                result = "home"
            elif ag > hg:
                result = "away"
            else:
                result = "draw"

        try:
            start_time = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

        return ExternalEvent(
            source=self.name,
            external_id=str(fid),
            sport="Football",
            event_name=event_name[:150],
            home=home.strip(),
            away=away.strip(),
            start_time=start_time,
            result=result,
            called_off=called_off,
            home_image=teams.get("home", {}).get("logo") or "",
            away_image=teams.get("away", {}).get("logo") or "",
            home_score=home_score,
            away_score=away_score,
        )


def _safe_float(val):
    if val is None:
        return None
    try:
        f = float(str(val).strip())
        return round(f, 2) if f > 0 else None
    except (ValueError, TypeError):
        return None


def _extract_api_football_odds(bookmakers):
    """Returns (home_odds, away_odds, draw_odds) from API-Football bookmakers list."""
    if not bookmakers or not isinstance(bookmakers, list):
        return None, None, None

    for bm in bookmakers:
        bets = bm.get("bets") or []
        for bet in bets:
            # Bet ID 1 is "Match Winner" (1X2)
            if bet.get("id") == 1 or str(bet.get("name", "")).lower() == "match winner":
                home, away, draw = None, None, None
                for val in bet.get("values") or []:
                    choice = str(val.get("value", "")).strip().lower()
                    odd_num = _safe_float(val.get("odd"))
                    if choice in ("home", "1"):
                        home = odd_num
                    elif choice in ("away", "2"):
                        away = odd_num
                    elif choice in ("draw", "x"):
                        draw = odd_num
                if home is not None or away is not None or draw is not None:
                    return home, away, draw

    return None, None, None


def _parse_h2h_encounter(item, team_a_name, team_b_name):
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    fixture = item.get("fixture", {})
    league = item.get("league", {})

    home_name = teams.get("home", {}).get("name", "")
    away_name = teams.get("away", {}).get("name", "")
    hg = goals.get("home")
    ag = goals.get("away")
    date_str = fixture.get("date", "")[:10]

    if hg is None or ag is None:
        return None

    score_str = f"{hg} - {ag}"
    winner_name = "Draw"
    winner_side = "D"

    # Identify whether home or away corresponds to team_a
    side_home = resolve_side(team_a_name, team_b_name, home_name)
    side_away = resolve_side(team_a_name, team_b_name, away_name)
    if side_home == "A" or side_away == "B":
        is_team_a_home = True
    elif side_home == "B" or side_away == "A":
        is_team_a_home = False
    else:
        is_team_a_home = team_a_name.lower() in home_name.lower()

    if hg > ag:
        winner_name = home_name
        winner_side = "A" if is_team_a_home else "B"
    elif ag > hg:
        winner_name = away_name
        winner_side = "B" if is_team_a_home else "A"

    return {
        "date": date_str,
        "competition": league.get("name", "Football"),
        "home": home_name,
        "away": away_name,
        "score": score_str,
        "winner": winner_name,
        "winner_side": winner_side,
    }


def _parse_form_fixture(item, target_team_name):
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    fixture = item.get("fixture", {})
    league = item.get("league", {})

    home_name = teams.get("home", {}).get("name", "")
    away_name = teams.get("away", {}).get("name", "")
    hg = goals.get("home")
    ag = goals.get("away")
    date_str = fixture.get("date", "")[:10]

    if hg is None or ag is None:
        return None

    s_home = match_score(target_team_name, home_name)
    s_away = match_score(target_team_name, away_name)
    is_home = (s_home >= s_away)
    opponent = away_name if is_home else home_name
    my_goals = hg if is_home else ag
    opp_goals = ag if is_home else hg

    if my_goals > opp_goals:
        res = "W"
    elif my_goals < opp_goals:
        res = "L"
    else:
        res = "D"

    return {
        "date": date_str,
        "opponent": opponent,
        "score": f"{hg} - {ag}",
        "result": res,
        "competition": league.get("name", ""),
    }
