"""Provider interface for importing fixtures and results from an external
sports data source.

A provider turns its source's data into ExternalEvent objects, so the sync
logic in predictions.services never depends on any one provider's format.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REQUEST_TIMEOUT = 15  # seconds

GENERIC_TOKENS = {
    "united", "city", "town", "club", "women", "men", "team", "national",
    "real", "inter", "athletic", "atletico", "sporting", "racing", "deportivo",
    "st", "saint", "north", "south", "east", "west", "central", "state",
    "u20", "u21", "u19", "u18", "u23",
}


def clean_team_name(name):
    """Normalize a team or player name by stripping country suffixes (e.g. '(Svk)', '(Gre)'),
    group label prefixes ('Last matches:'), asterisks, club abbreviations, and excess whitespace.
    """
    if not name:
        return ""
    s = str(name).strip().lstrip("*").strip()
    s = re.sub(r"\s*\([A-Za-z0-9/ ]+\)\s*", " ", s)
    s = re.sub(r"^(?:last\s+matches\s*:?\s*)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\b(?:fc|cf|sc|ac|fk|sk|bk)\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s.lower()


def match_score(team_name, candidate_name):
    """Score how well candidate_name matches team_name (0 to 100).
    Handles exact matches, substring containment, and distinctive word token overlap.
    """
    t = clean_team_name(team_name)
    c = clean_team_name(candidate_name)
    if not t or not c:
        return 0
    if t == c:
        return 100
    if t in c or c in t:
        return 80

    t_tokens = set(re.findall(r"[a-z0-9]{3,}", t))
    c_tokens = set(re.findall(r"[a-z0-9]{3,}", c))
    if not t_tokens or not c_tokens:
        return 0

    overlap = t_tokens & c_tokens
    distinctive_overlap = overlap - GENERIC_TOKENS
    if distinctive_overlap:
        return 60 + 10 * len(distinctive_overlap)
    elif overlap:
        return 20 + 5 * len(overlap)
    return 0


def resolve_side(team_a_name, team_b_name, candidate_name):
    """Determine whether candidate_name refers to Team A or Team B.
    Returns 'A', 'B', or None if unresolved.
    """
    sa = match_score(team_a_name, candidate_name)
    sb = match_score(team_b_name, candidate_name)
    if sa > sb and sa >= 30:
        return "A"
    elif sb > sa and sb >= 30:
        return "B"
    return None



class ProviderError(Exception):
    """The external source could not be reached or returned bad data."""


@dataclass
class ExternalEvent:
    source: str
    external_id: str
    sport: str  # our Sport.name, e.g. "Football"
    event_name: str
    home: str
    away: str
    start_time: datetime  # timezone-aware
    # "home", "away", "draw", or None while there is no final result.
    result: str | None = None
    # True if the source reports the match postponed/cancelled/abandoned.
    called_off: bool = False
    home_image: str = ""
    away_image: str = ""
    home_score: str = ""
    away_score: str = ""
    home_odds: float | None = None
    away_odds: float | None = None
    draw_odds: float | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class H2HSummary:
    team_a_wins: int = 0
    team_b_wins: int = 0
    draws: int = 0
    total_matches: int = 0
    # List of past encounters between the two teams
    past_matches: list = field(default_factory=list)
    # Team A last 5 matches: [{"date": "...", "opponent": "...", "score": "...", "result": "W"|"D"|"L", "competition": "..."}, ...]
    team_a_form: list = field(default_factory=list)
    # Team B last 5 matches
    team_b_form: list = field(default_factory=list)


class Provider:
    """Base class. Subclasses set `name` and implement the fetch methods."""

    name = ""

    def supports(self, sport_name):
        raise NotImplementedError

    def fetch_fixtures(self, sport_name, days_ahead, new_day_only=False, with_odds=False):
        """Upcoming events for `sport_name`, as a list of ExternalEvent.

        new_day_only: only the day `days_ahead` days from today, for daily
        runs whose earlier days were already imported."""
        raise NotImplementedError

    def fetch_odds(self, sport_name, indent_days=0):
        """{external_id: (home_odds, away_odds, draw_odds)} for events on indent_days.
        Default implementation returns empty dict."""
        return {}

    def fetch_event_odds(self, external_id):
        """(home_odds, away_odds, draw_odds) for a single event, or None."""
        return None

    def fetch_matches_odds(self, matches):
        """{match.pk: (home_odds, away_odds, draw_odds)} for an iterable of matches."""
        results = {}
        for match in matches:
            ext_id = getattr(match, "external_id", "")
            if ext_id:
                odds = self.fetch_event_odds(ext_id)
                if odds and (odds[0] is not None or odds[1] is not None or odds[2] is not None):
                    results[match.pk] = odds
        return results

    def fetch_results(self, sport_name, kickoffs):
        """{external_id: ExternalEvent} for as many of `kickoffs`
        ({external_id: start_time}) as the source knows about. Events
        without a final result have result=None."""
        raise NotImplementedError

    def fetch_h2h_and_form(self, match):
        """Fetch Head-to-Head encounters and recent form for the given Match object.

        Returns an H2HSummary instance or None.
        """
        return None

    def fetch_image(self, url):
        """Raw bytes of an image URL (team logo/flag), or None on failure.

        Uses a plain request, not the provider's session, so API keys in the
        session headers are never sent to the image host."""
        if not url.startswith("https://"):
            return None
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException:
            return None
        return response.content or None


def make_session(headers=None):
    """A requests session that retries transient failures (5xx, 429)."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    if headers:
        session.headers.update(headers)
    return session
