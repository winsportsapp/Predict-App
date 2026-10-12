from django import template
from django.templatetags.static import static
from django.utils.html import format_html

from ..locations import COUNTRY_CODES

register = template.Library()


@register.filter
def signed_points(value):
    """Points with an explicit sign: 10 -> "+10", -5 -> "-5", 0 -> "0"."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    return f"+{number}" if number > 0 else str(number)


@register.simple_tag
def team_flag(team, css_class="team-flag"):
    """Render a small flag <img> for `team`, or nothing if it has none.

    Centralised so every page shows the same fixed-size markup and a team
    with no uploaded flag never renders a broken image.
    """
    if not team or not getattr(team, "flag", None):
        return ""
    try:
        url = team.flag.url
    except ValueError:
        return ""
    return format_html(
        '<img src="{}" alt="{} flag" class="{}">',
        url,
        team.name,
        css_class,
    )


@register.simple_tag
def country_flag(country, css_class="team-flag"):
    """Render a small flag <img> for a Profile.country name, or nothing if
    it is blank or not a supported country. Same size as team flags."""
    code = COUNTRY_CODES.get(country)
    if not code:
        return ""
    return format_html(
        '<img src="{}" alt="{} flag" class="{}">',
        static(f"predictions/flags/{code}.svg"),
        country,
        css_class,
    )


@register.filter
def podium_slots(profiles):
    """Return 3 podium slot dicts (Gold, Silver, Bronze).
    If an eligible player earned that medal, slot['profile'] is set to that player.
    Otherwise, slot['profile'] is None (rendered as 'Awaiting' in the podium).
    """
    slots = [
        {"place": "1st Place", "medal": "gold", "profile": None},
        {"place": "2nd Place", "medal": "silver", "profile": None},
        {"place": "3rd Place", "medal": "bronze", "profile": None},
    ]
    if not profiles:
        return slots
    for p in profiles:
        medal = getattr(p, "medal", None)
        if medal == "gold" and slots[0]["profile"] is None:
            slots[0]["profile"] = p
        elif medal == "silver" and slots[1]["profile"] is None:
            slots[1]["profile"] = p
        elif medal == "bronze" and slots[2]["profile"] is None:
            slots[2]["profile"] = p
    return slots

