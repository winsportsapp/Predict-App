"""Centralized service for tracking, recording, and displaying real-time API credit
balances for API-Football and FlashLive (Primary & Secondary RapidAPI keys).
"""

import logging
from datetime import datetime, timedelta, timezone as dt_timezone
import requests
from django.conf import settings
from django.utils import timezone

from .models import APICreditStatus

logger = logging.getLogger(__name__)

IST = dt_timezone(timedelta(hours=5, minutes=30))
FLASHLIVE_HOST = "flashlive-sports.p.rapidapi.com"


def _format_datetime_ist(dt):
    if not dt:
        return ""
    if timezone.is_aware(dt):
        ist_dt = dt.astimezone(IST)
    else:
        ist_dt = dt.replace(tzinfo=dt_timezone.utc).astimezone(IST)
    now_ist = datetime.now(dt_timezone.utc).astimezone(IST)
    if ist_dt.date() == now_ist.date():
        return f"Today at {ist_dt.strftime('%I:%M %p IST')}"
    return ist_dt.strftime("%b %d at %I:%M %p IST")


def _parse_rapidapi_reset(headers, default_date_str="October 25 at 03:05 PM IST"):
    reset_val = None
    if isinstance(headers, (dict, requests.structures.CaseInsensitiveDict)):
        for k, v in headers.items():
            if str(k).lower() in ("x-ratelimit-requests-reset", "ratelimit-reset"):
                reset_val = v
                break
    if reset_val:
        try:
            secs = int(reset_val)
            reset_dt = datetime.now(dt_timezone.utc) + timedelta(seconds=secs)
            ist_dt = reset_dt.astimezone(IST)
            return ist_dt.strftime("%B %d at %I:%M %p IST")
        except Exception:
            pass
    return default_date_str


def record_provider_headers(provider_name, headers):
    """Update APICreditStatus from live HTTP response headers."""
    if not headers or not isinstance(headers, (dict, requests.structures.CaseInsensitiveDict)):
        return

    hdr_map = {str(k).lower(): str(v) for k, v in headers.items()}

    try:
        if provider_name in ("flashlive_primary", "flashlive_secondary"):
            choice = (
                APICreditStatus.ProviderChoice.FLASHLIVE_PRIMARY
                if provider_name == "flashlive_primary"
                else APICreditStatus.ProviderChoice.FLASHLIVE_SECONDARY
            )
            rem_str = hdr_map.get("x-ratelimit-requests-remaining")
            lim_str = hdr_map.get("x-ratelimit-requests-limit")
            rem = int(rem_str) if rem_str and rem_str.lstrip("-").isdigit() else None
            lim = int(lim_str) if lim_str and lim_str.isdigit() else 500
            if rem is not None and rem < 0:
                rem = 0

            default_date = (
                "October 25 at 03:05 PM IST"
                if provider_name == "flashlive_primary"
                else "November 13 at 08:00 PM IST"
            )
            reset_date_str = _parse_rapidapi_reset(headers, default_date)

            defaults = {
                "monthly_remaining": rem,
                "monthly_limit": lim,
                "reset_info": f"Quota restores on {reset_date_str}",
                "raw_headers": {k: v for k, v in hdr_map.items() if "ratelimit" in k},
            }
            APICreditStatus.objects.update_or_create(
                provider=choice,
                defaults=defaults,
            )
    except Exception as exc:
        logger.debug("Could not record provider headers for %s: %s", provider_name, exc)


def fetch_live_flashlive_credits(key_name="secondary"):
    """Query FlashLive /v1/sports/list to capture live RapidAPI quota headers."""
    key = (
        getattr(settings, "RAPIDAPI_KEY", "")
        if key_name == "primary"
        else getattr(settings, "RAPIDAPI_STATS_KEY", "")
    )
    if not key:
        return

    try:
        resp = requests.get(
            f"https://{FLASHLIVE_HOST}/v1/sports/list",
            headers={"x-rapidapi-key": key, "x-rapidapi-host": FLASHLIVE_HOST},
            timeout=8,
        )
        record_provider_headers(f"flashlive_{key_name}", resp.headers)
    except Exception as exc:
        logger.warning("Error querying FlashLive (%s key): %s", key_name, exc)


def get_api_credits_display_summary(force_refresh=False):
    """Return dictionary with badge classes and formatted texts for the FlashLive API balances."""
    primary_status = APICreditStatus.objects.filter(
        provider=APICreditStatus.ProviderChoice.FLASHLIVE_PRIMARY
    ).first()
    secondary_status = APICreditStatus.objects.filter(
        provider=APICreditStatus.ProviderChoice.FLASHLIVE_SECONDARY
    ).first()

    # Initial seeding or forced manual refresh
    if force_refresh or not primary_status:
        fetch_live_flashlive_credits("primary")
        primary_status = APICreditStatus.objects.filter(
            provider=APICreditStatus.ProviderChoice.FLASHLIVE_PRIMARY
        ).first()

    if force_refresh or not secondary_status:
        fetch_live_flashlive_credits("secondary")
        secondary_status = APICreditStatus.objects.filter(
            provider=APICreditStatus.ProviderChoice.FLASHLIVE_SECONDARY
        ).first()

    # Format 2. FlashLive Primary API Monthly
    pri_rem = primary_status.monthly_remaining if primary_status else None
    pri_lim = primary_status.monthly_limit if primary_status else 500
    pri_info = primary_status.reset_info if primary_status and primary_status.reset_info else "Quota restores on October 25 at 03:05 PM IST"
    if pri_rem is None or pri_rem == 0:
        pri_badge = f"0 / {pri_lim} Monthly (Exhausted)"
        pri_class = "badge-exceeded"
    elif pri_rem <= 50:
        pri_badge = f"{pri_rem} / {pri_lim} Monthly (Low)"
        pri_class = "badge-low"
    else:
        pri_badge = f"{pri_rem} / {pri_lim} Monthly"
        pri_class = "badge-ok"

    pri_updated = _format_datetime_ist(primary_status.last_checked) if primary_status else ""
    flashlive_primary_data = {
        "badge_text": pri_badge,
        "badge_class": pri_class,
        "detail": f"Monthly limit: {pri_lim} requests • {pri_info}",
        "last_updated": pri_updated,
    }

    # Format 3. FlashLive Secondary API Monthly
    sec_rem = secondary_status.monthly_remaining if secondary_status else None
    sec_lim = secondary_status.monthly_limit if secondary_status else 500
    sec_info = secondary_status.reset_info if secondary_status and secondary_status.reset_info else "Quota restores on November 13 at 08:00 PM IST"
    if sec_rem is None:
        sec_badge = f"Active / {sec_lim} Monthly"
        sec_class = "badge-ok"
    elif sec_rem == 0:
        sec_badge = f"0 / {sec_lim} Monthly (Exhausted)"
        sec_class = "badge-exceeded"
    elif sec_rem <= 50:
        sec_badge = f"{sec_rem} / {sec_lim} Monthly (Low)"
        sec_class = "badge-low"
    else:
        sec_badge = f"{sec_rem} / {sec_lim} Monthly"
        sec_class = "badge-ok"

    sec_updated = _format_datetime_ist(secondary_status.last_checked) if secondary_status else ""
    flashlive_secondary_data = {
        "badge_text": sec_badge,
        "badge_class": sec_class,
        "detail": f"Monthly limit: {sec_lim} requests • {sec_info}",
        "last_updated": sec_updated,
    }

    return {
        "flashlive_primary": flashlive_primary_data,
        "flashlive_secondary": flashlive_secondary_data,
    }
