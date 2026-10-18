from django.conf import settings

from .flashlive import FlashLiveProvider


def get_providers():
    """The providers that are configured (have an API key), in priority order.

    FlashLive handles all sports: Football, Cricket, Tennis, Badminton, Hockey.
    """
    providers = []
    if getattr(settings, "RAPIDAPI_KEY", "") or getattr(settings, "RAPIDAPI_STATS_KEY", ""):
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

