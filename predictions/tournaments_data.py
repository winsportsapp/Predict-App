"""
Upcoming Sports Tournaments Calendar Data
=========================================
Manually verified ~35–40 day outlook of major tournaments aligned strictly with
WinSports' supported tournament filter presets (predictions/admin.py: SPORT_TOURNAMENT_PRESETS).
Requires zero database models, tables, or migrations.

Monthly Update Procedure:
-------------------------
1. Open this file (predictions/tournaments_data.py).
2. Update LAST_UPDATED to the current review date.
3. Update CALENDAR_PERIOD to reflect the upcoming ~35–40 day window.
4. Remove tournaments whose dates have elapsed.
5. Add/update upcoming tournaments across Football, Cricket, Tennis, Badminton, Hockey.
   CRITICAL: Only include competitions matching WinSports' supported filter presets.
6. Verify official URLs and mark tentative schedules as 'Dates to be confirmed'.
7. Run tests: `python manage.py test predictions.tests_sports_insights_static`.
"""

from typing import Any, Dict, List, Optional

LAST_UPDATED = "November 3, 2026"
CALENDAR_PERIOD = "November 3 – Mid-December 2026 (~35–40 Day Outlook)"
DISCLAIMER = (
    "This calendar is a curated, manually verified informational schedule of major sports events "
    "matching WinSports' supported tournament categories over the next ~35–40 days. It is compiled independently "
    "for sports fans. WinSports prioritizes tournaments with confirmed upcoming prediction fixtures in our database; "
    "filter-supported competitions without open prediction fixtures are clearly labeled with fixtures not confirmed."
)

TOURNAMENTS_DATA: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # FOOTBALL (Supported via SPORT_TOURNAMENT_PRESETS["football"]["popular_chips"])
    # -------------------------------------------------------------------------
    {
        "name": "UEFA Champions League (League Phase Matchdays 4 & 5)",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "supported_filter": "UEFA Champions League",
        "dates": "November 3–4 & November 24–25, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": True,
        "winsports_fixtures_status": "Confirmed upcoming fixtures",
        "location": "Europe (Multiple Venues)",
        "format": "36-Team Unified League Stage",
        "description": "Crucial mid-stage fixtures in European club football's flagship competition under the 36-team single table format, determining direct qualification for the Round of 16.",
        "official_url": "https://www.uefa.com/uefachampionsleague/fixtures-results/",
    },
    {
        "name": "Indian Super League (ISL) Regular Season",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "supported_filter": "India: Indian Super League",
        "dates": "November 2026 (Regular Season Matchdays)",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "India (Home & Away Venues)",
        "format": "Tier 1 Domestic League",
        "description": "India's premier domestic football competition featuring intense rivalries as clubs battle for playoff seeding and the ISL League Shield.",
        "official_url": "https://www.indiansuperleague.com/schedule-fixtures",
    },
    {
        "name": "English Premier League",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "supported_filter": "England: Premier League",
        "dates": "November 6–8, 21–23, 27–29, 2026 (Matchdays 11–13)",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "England (Multiple Venues)",
        "format": "Tier 1 Domestic League (20 Clubs)",
        "description": "England's premier domestic league featuring weekly marquee fixtures across November as top clubs contend for the title and European spots.",
        "official_url": "https://www.premierleague.com/fixtures",
    },
    {
        "name": "Spanish LaLiga",
        "sport": "football",
        "sport_display": "Football",
        "sport_icon": "⚽",
        "supported_filter": "Spain: LaLiga",
        "dates": "November 6–8, 20–22, 27–29, 2026 (Matchdays 12–14)",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Spain (Multiple Venues)",
        "format": "Tier 1 Domestic League (20 Clubs)",
        "description": "Spain's top-tier league featuring high-stakes domestic title and European qualification clashes throughout November.",
        "official_url": "https://www.laliga.com/en-GB/laliga-easports/results",
    },

    # -------------------------------------------------------------------------
    # CRICKET (Supported via SPORT_TOURNAMENT_PRESETS["cricket"]["popular_chips"])
    # -------------------------------------------------------------------------
    {
        "name": "India Tour of New Zealand (White-Ball Series)",
        "sport": "cricket",
        "sport_display": "Cricket",
        "sport_icon": "🏏",
        "supported_filter": "*One Day International*",
        "dates": "November 1 – November 15, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": True,
        "winsports_fixtures_status": "Confirmed upcoming fixtures",
        "location": "New Zealand (Auckland, Wellington, Hamilton, Tauranga)",
        "format": "Bilateral Limited-Overs Series (T20Is & ODIs)",
        "description": "India's premier white-ball tour featuring T20I and ODI bilateral fixtures against New Zealand.",
        "official_url": "https://www.bcci.tv/international/fixtures",
    },
    {
        "name": "England Tour of Australia (Bilateral ODI & T20I Series)",
        "sport": "cricket",
        "sport_display": "Cricket",
        "sport_icon": "🏏",
        "supported_filter": "*One Day International*",
        "dates": "November 13 – November 29, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Australia (Perth, Adelaide, Melbourne, Sydney)",
        "format": "Bilateral Limited-Overs Series (ODIs & T20Is)",
        "description": "High-profile white-ball bilateral series between England and Australia spanning One Day Internationals and Twenty20 Internationals.",
        "official_url": "https://www.cricket.com.au/fixtures",
    },
    {
        "name": "Ranji Trophy (Elite Group Stage)",
        "sport": "cricket",
        "sport_display": "Cricket",
        "sport_icon": "🏏",
        "supported_filter": "*Ranji Trophy*",
        "dates": "October 11 – November 5, 2026 (Phase 1 Concluding Rounds)",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "India (Multiple Venues)",
        "format": "Premier First-Class Domestic Championship",
        "description": "India's celebrated domestic first-class championship; Phase 1 league fixtures conclude in early November before the domestic tournament pauses for white-ball cups until Phase 2 resumes in January.",
        "official_url": "https://www.bcci.tv/domestic/fixtures",
    },

    # -------------------------------------------------------------------------
    # TENNIS (Supported via SPORT_TOURNAMENT_PRESETS["tennis"]["popular_chips"])
    # -------------------------------------------------------------------------
    {
        "name": "Rolex Paris Masters (ATP Masters 1000)",
        "sport": "tennis",
        "sport_display": "Tennis",
        "sport_icon": "🎾",
        "supported_filter": "*Masters*",
        "dates": "November 2 – November 8, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": True,
        "winsports_fixtures_status": "Confirmed upcoming fixtures",
        "location": "Paris, France (Paris La Défense Arena)",
        "format": "ATP Masters 1000 (Indoor Hard Court)",
        "description": "The season's final ATP Masters 1000 indoor event featuring the world's top ranked men's players battling for the prestigious title and crucial year-end ranking points.",
        "official_url": "https://www.atptour.com/en/tournaments/paris/352/overview",
    },
    {
        "name": "Nitto ATP Finals (Turin 2026)",
        "sport": "tennis",
        "sport_display": "Tennis",
        "sport_icon": "🎾",
        "supported_filter": "*ATP Finals*",
        "dates": "November 15 – November 22, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Turin, Italy (Inalpi Arena)",
        "format": "Indoor Hard Court (Top 8 Singles & Doubles)",
        "description": "The season-ending ATP championship featuring the world's top 8 qualified men's singles players and doubles pairings competing in round-robin and knockout ties.",
        "official_url": "https://www.atptour.com/en/tournaments/nitto-atp-finals/605/overview",
    },

    # -------------------------------------------------------------------------
    # BADMINTON (Supported via SPORT_TOURNAMENT_PRESETS["badminton"]["popular_chips"])
    # -------------------------------------------------------------------------
    {
        "name": "Korea Open (BWF Super 500)",
        "sport": "badminton",
        "sport_display": "Badminton",
        "sport_icon": "🏸",
        "supported_filter": "*Korea Open*",
        "dates": "November 3 – November 8, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": True,
        "winsports_fixtures_status": "Confirmed upcoming fixtures",
        "location": "Yeosu, South Korea (Jinnam Stadium)",
        "format": "BWF World Tour Super 500",
        "description": "Official BWF World Tour Super 500 event offering vital world ranking points and qualifying positions for the year-end World Tour Finals.",
        "official_url": "https://bwfworldtour.bwfbadminton.com/tournaments/",
    },
    {
        "name": "Kumamoto Masters Japan (BWF Super 500)",
        "sport": "badminton",
        "sport_display": "Badminton",
        "sport_icon": "🏸",
        "supported_filter": "*Super 500*",
        "dates": "November 10 – November 15, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Kumamoto, Japan (Kumamoto Gymnasium)",
        "format": "BWF World Tour Super 500",
        "description": "Key BWF World Tour Super 500 event offering crucial world ranking points and qualifying positions for the year-end World Tour Finals.",
        "official_url": "https://bwfworldtour.bwfbadminton.com/tournaments/",
    },
    {
        "name": "Hong Kong Open (BWF Super 500)",
        "sport": "badminton",
        "sport_display": "Badminton",
        "sport_icon": "🏸",
        "supported_filter": "*Hong Kong Open*",
        "dates": "November 17 – November 22, 2026",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Hong Kong, China (Kai Tak Arena)",
        "format": "BWF World Tour Super 500",
        "description": "Premier Asian leg BWF Super 500 championship drawing the world's top shuttlers in the final qualification push before the Finals.",
        "official_url": "https://bwfworldtour.bwfbadminton.com/tournaments/",
    },

    # -------------------------------------------------------------------------
    # HOCKEY (Supported via SPORT_TOURNAMENT_PRESETS["hockey"]["popular_chips"])
    # -------------------------------------------------------------------------
    {
        "name": "FIH Hockey Pro League — 2026/27 Stage 1",
        "sport": "hockey",
        "sport_display": "Hockey",
        "sport_icon": "🏑",
        "supported_filter": "*Pro League*",
        "dates": "December 8 – December 13, 2026 (Argentina Leg)",
        "status": "Confirmed",
        "has_upcoming_fixtures": False,
        "winsports_fixtures_status": "Upcoming WinSports fixtures not confirmed",
        "location": "Córdoba, Argentina (Estadio Municipal de Hockey)",
        "format": "Global National Teams League (Men & Women)",
        "description": "The opening block of the FIH Pro League season featuring top-tier international fixtures with Olympic qualification implications.",
        "official_url": "https://www.fih.hockey/events/fih-pro-league",
    },
]


def get_upcoming_tournaments(sport_slug: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return tournaments filtered by sport, prioritizing those with confirmed upcoming WinSports fixtures."""
    if not sport_slug or sport_slug == "all":
        data = TOURNAMENTS_DATA
    else:
        data = [t for t in TOURNAMENTS_DATA if t["sport"] == sport_slug.lower()]
    # Prioritize tournaments with confirmed upcoming WinSports fixtures first
    return sorted(data, key=lambda t: 0 if t.get("has_upcoming_fixtures") else 1)


def get_calendar_metadata() -> Dict[str, str]:
    """Return calendar period and last updated timestamp."""
    return {
        "last_updated": LAST_UPDATED,
        "calendar_period": CALENDAR_PERIOD,
        "disclaimer": DISCLAIMER,
        "total_tournaments": str(len(TOURNAMENTS_DATA)),
    }


def get_tournament_sports_categories() -> List[Dict[str, Any]]:
    """Return available sports categories with tournament counts for filter pills."""
    sports = [
        {"slug": "all", "name": "All Sports", "icon": "🌐"},
        {"slug": "cricket", "name": "Cricket", "icon": "🏏"},
        {"slug": "football", "name": "Football", "icon": "⚽"},
        {"slug": "tennis", "name": "Tennis", "icon": "🎾"},
        {"slug": "badminton", "name": "Badminton", "icon": "🏸"},
        {"slug": "hockey", "name": "Hockey", "icon": "🏑"},
    ]
    for s in sports:
        if s["slug"] == "all":
            s["count"] = len(TOURNAMENTS_DATA)
        else:
            s["count"] = len([t for t in TOURNAMENTS_DATA if t["sport"] == s["slug"]])
    return sports
