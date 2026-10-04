"""Supported countries and their states for signup.

A fixed, curated list (not a general-purpose geo database) covering the
countries this app supports -- India only: prizes are for India residents,
and players elsewhere can still sign in with Google and leave country
blank. Both fields are stored as plain display text on Profile (e.g.
country="India", state="Kerala") rather than codes, so admin screens and
the leaderboard need no extra lookup to be readable. Profiles saved before
other countries were removed keep their value; it just shows no flag.
"""

STATES_BY_COUNTRY = {
    # Assam, Andhra Pradesh, Odisha, Nagaland, Sikkim and Telangana are
    # deliberately left out: residents can't claim prizes (Terms section 1).
    "India": [
        "Arunachal Pradesh",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Punjab",
        "Rajasthan",
        "Tamil Nadu",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Andaman and Nicobar Islands",
        "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi (National Capital Territory)",
        "Jammu and Kashmir",
        "Ladakh",
        "Lakshadweep",
        "Puducherry",
    ],
}

COUNTRIES = list(STATES_BY_COUNTRY.keys())
COUNTRY_CHOICES = [(name, name) for name in COUNTRIES]

# ISO 3166 alpha-2 code per country, naming its flag SVG in
# static/predictions/flags/ (shown before player names on the leaderboard).
COUNTRY_CODES = {
    "India": "in",
}

# Every state across every country, for the state field's ChoiceField.choices
# (which must accept whichever state a valid POST names, whatever the
# selected country). The cross-field check that the state actually belongs
# to the chosen country happens separately, in RegistrationForm.clean().
_ALL_STATES = sorted({state for states in STATES_BY_COUNTRY.values() for state in states})
STATE_CHOICES = [(name, name) for name in _ALL_STATES]


def states_for(country):
    """The valid state list for `country`, or [] if it isn't supported."""
    return STATES_BY_COUNTRY.get(country, [])
