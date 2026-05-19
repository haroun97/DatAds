from collections.abc import Callable

from app.pollers.base import BasePoller
from app.pollers.facebook import FACEBOOK_CAMPAIGNS, FacebookPoller
from app.pollers.google import GooglePoller
from app.pollers.tiktok import TikTokPoller

PLATFORM_CAMPAIGNS: dict[str, list[str]] = {
    "facebook": FACEBOOK_CAMPAIGNS,
    "google": [],
    "tiktok": [],
}

_POLLER_FACTORIES: dict[str, Callable[[], BasePoller]] = {
    "facebook": FacebookPoller,
    "google": GooglePoller,
    "tiktok": TikTokPoller,
}

IMPLEMENTED_PLATFORMS = frozenset({"facebook"})


def campaign_ids_for(platform: str) -> list[str]:
    return list(PLATFORM_CAMPAIGNS.get(platform, []))


def create_poller(platform: str) -> BasePoller:
    factory = _POLLER_FACTORIES.get(platform)
    if factory is None:
        raise ValueError(f"Unknown platform: {platform}")
    return factory()
