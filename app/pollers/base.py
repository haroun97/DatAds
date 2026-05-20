# Abstract base class that every ad-platform poller must implement.
# Adding a new platform = creating a subclass and implementing fetch().

from abc import ABC, abstractmethod
from datetime import date

from app.schemas.ad_performance import AdPerformanceCreate


class BasePoller(ABC):
    # Each subclass must set this to the platform name (e.g. "facebook").
    platform: str

    @abstractmethod
    def fetch(self, since: date, until: date, **kwargs) -> list[AdPerformanceCreate]:
        """Fetch and normalize all records for the given date range."""
