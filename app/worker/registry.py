# Central registry that maps platform names to their poller classes and campaign lists.
# Add new platforms here once their pollers are implemented.

from collections.abc import Callable

from app.pollers.base import BasePoller
from app.pollers.facebook import FACEBOOK_CAMPAIGNS, FacebookPoller
from app.pollers.google import GooglePoller
from app.pollers.tiktok import TikTokPoller

# Default campaign IDs used when a platform job doesn't specify them explicitly.
PLATFORM_CAMPAIGNS: dict[str, list[str]] = {
    "facebook": FACEBOOK_CAMPAIGNS,
    "google": [],    # no campaigns configured until GooglePoller is implemented
    "tiktok": [],    # no campaigns configured until TikTokPoller is implemented
}

# Maps each platform name to its poller constructor (called with no arguments).
_POLLER_FACTORIES: dict[str, Callable[[], BasePoller]] = {
    "facebook": FacebookPoller,
    "google": GooglePoller,
    "tiktok": TikTokPoller,
}

# Only platforms in this set will actually be processed; others are logged and skipped.
IMPLEMENTED_PLATFORMS = frozenset({"facebook"})


def campaign_ids_for(platform: str) -> list[str]:
    # Returns the configured campaign IDs for a platform, or an empty list if unknown.
    return list(PLATFORM_CAMPAIGNS.get(platform, []))


def create_poller(platform: str) -> BasePoller:
    # Instantiate and return the correct poller for the given platform name.
    factory = _POLLER_FACTORIES.get(platform)
    if factory is None:
        raise ValueError(f"Unknown platform: {platform}")
    return factory()
