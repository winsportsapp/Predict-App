from django.conf import settings

from .api_football import APIFootballProvider
from .flashlive import FlashLiveProvider


def get_providers():
    """The providers that are configured (have an API key), in priority order.

    API-Football is prioritized for Football when API_FOOTBALL_KEY is set.
    FlashLive handles other sports (Cricket, Tennis, Badminton, Hockey) and acts
    as a fallback.
    """
    providers = []
    if getattr(settings, "API_FOOTBALL_KEY", ""):
        providers.append(APIFootballProvider())
    if getattr(settings, "RAPIDAPI_KEY", ""):
        providers.append(FlashLiveProvider())
    return providers


def provider_for(sport_name, providers=None, check_active=False):
    """The first configured provider that covers `sport_name`, or None.

    If check_active is True and the Sport has is_active=False in the database,
    returns None to guarantee 0 API calls.
    """
    if check_active:
        from predictions.models import Sport

        sport = Sport.objects.filter(name__iexact=sport_name).first()
        if sport and not sport.is_active:
            return None

    for provider in providers if providers is not None else get_providers():
        if provider.supports(sport_name):
            return provider
    return None

