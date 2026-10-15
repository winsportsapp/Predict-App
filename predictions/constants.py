"""Sport names for the public navigation.

Migrations 0007_create_default_sports and 0009_create_hockey_sport seed these
as Sport rows. Kept separate from those migrations (which hardcode their own
copies) so future edits here can't silently change already-applied migration
history.
"""

SUPPORTED_SPORTS = ["Football", "Cricket", "Tennis", "Badminton", "Hockey"]
SPORT_SLUGS = {name.lower(): name for name in SUPPORTED_SPORTS}
DEFAULT_SPORT_SLUG = "football"

# Sports whose matches can end in a draw; only these offer a "Draw" pick.
DRAW_SPORTS = frozenset({"Football", "Cricket", "Hockey"})

# Standard second division, youth, and reserve tournament / team exclusion patterns for Football.
DEFAULT_FOOTBALL_SECOND_DIV_EXCLUDES = frozenset({
    # Second tiers & lower divisions
    "*premier league 2*",
    "*ligue 2*",
    "*laliga 2*",
    "*laliga2*",
    "*2. bundesliga*",
    "*2.bundesliga*",
    "*serie b*",
    "*serie c*",
    "*segunda*",
    "*championship*",
    "*division 2*",
    "*2nd division*",
    "*second division*",
    "*2. division*",
    "*2. liga*",
    "*eerste divisie*",
    "*primera b*",
    "*league one*",
    "*league two*",
    "*1. lig*",
    "*j2 league*",
    "*k league 2*",
    "*super league 2*",
    # Youth and Reserves
    "*res.*",
    "*reserve*",
    "*reserves*",
    "*u23*",
    "*u21*",
    "*u20*",
    "*u19*",
    "*u18*",
    "*u17*",
    "*youth*",
    # Women's football
    "*women*",
    "*feminin*",
    # Reserve / B teams
    "*b team*",
    "* ii*",
})


def is_fixture_excluded(sport_name, keys, custom_excludes=None):
    """Return True if any key matches exclusion patterns (custom or default football excludes)."""
    from fnmatch import fnmatchcase

    excludes = set()
    if custom_excludes:
        if isinstance(custom_excludes, str):
            patterns = [
                p.strip().strip('"\'')
                for p in custom_excludes.replace("\r\n", "\n").replace("\n", ",").split(",")
                if p.strip().strip('"\'')
            ]
        else:
            patterns = custom_excludes
        excludes.update(str(p).strip().lower() for p in patterns if str(p).strip())

    if str(sport_name).strip().lower() == "football":
        excludes.update(DEFAULT_FOOTBALL_SECOND_DIV_EXCLUDES)

    if not excludes:
        return False

    normalized_keys = [str(k).strip().lower() for k in keys if k]
    for pat in excludes:
        p = str(pat).strip().lower()
        if not p:
            continue
        for key in normalized_keys:
            if fnmatchcase(key, p):
                return True
            if "*" not in p and "?" not in p and p in key:
                return True
    return False


