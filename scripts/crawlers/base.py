"""Base crawler interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCrawler(ABC):
    def __init__(self, source: dict[str, Any]) -> None:
        self.source = source

    @abstractmethod
    def crawl(self) -> list[dict]:
        """Return normalized candidate-like dictionaries."""
