from abc import ABC, abstractmethod
from datetime import date

from app.schemas.ad_performance import AdPerformanceCreate


class BasePoller(ABC):
    platform: str

    @abstractmethod
    def fetch(self, since: date, until: date, **kwargs) -> list[AdPerformanceCreate]:
        """Fetch and normalize all records for the given date range."""
