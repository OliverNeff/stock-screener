"""Datenmodelle fuer die Aktienbeobachtungsanwendung."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class StockQuote:
    """Aktueller Kurs einer Aktie."""

    symbol: str
    name: str = ""
    current_price: float | None = None
    previous_close: float | None = None
    open_price: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    price_change_pct: float | None = None
    volume: int | None = None
    market_cap: float | None = None
    week52_high: float | None = None
    week52_low: float | None = None
    currency: str = "USD"
    last_updated: datetime | None = None


@dataclass
class StockChart:
    """Zeitreihendaten fuer ein Aktienkurs-Chart."""

    symbol: str
    dates: list[str] = None  # type: ignore[assignment]
    prices: list[float] = None  # type: ignore[assignment]
    period: str = "1mo"

    def __post_init__(self) -> None:
        if self.dates is None:
            self.dates = []
        if self.prices is None:
            self.prices = []


@dataclass
class WatchlistItem:
    """Ein Eintrag in der Watchlist."""

    symbol: str
    display_name: str = ""
    added_at: datetime | None = None
