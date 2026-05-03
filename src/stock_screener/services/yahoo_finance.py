"""Yahoo Finance Daten-Service.

Kapselt alle yfinance-API-Aufrufe und liefert strukturierte Daten.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yfinance as yf

from stock_screener.models.stock import StockChart, StockQuote

logger = logging.getLogger(__name__)

# Pfad zur eingebetteten Ticker-Liste
_TICKERS_PATH = Path(__file__).resolve().parents[3] / "data" / "tickers.json"


def _load_tickers() -> list[dict[str, str]]:
    """Eingebettete Ticker-Liste laden."""
    try:
        with open(_TICKERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.warning("Ticker-Liste nicht gefunden: %s", exc)
        return []


class YahooFinanceService:
    """Bietet Zugriff auf Aktienkurse ueber Yahoo Finance (yfinance)."""

    def __init__(self) -> None:
        self._tickers: list[dict[str, str]] = []

    def refresh_ticker_list(self) -> None:
        """Eingebettete Ticker-Liste neu laden."""
        self._tickers = _load_tickers()

    def search(self, query: str) -> list[dict[str, str]]:
        """Aktien anhand von Symbol oder Firmenname suchen."""
        if not query or len(query) < 1:
            return []

        query_upper = query.upper().strip()
        results = []

        for ticker in self._tickers:
            symbol = ticker.get("symbol", "")
            name = ticker.get("name", "")
            if query_upper in symbol or query_upper in name.upper():
                results.append(ticker)

        return results

    def fetch_quote(self, symbol: str) -> StockQuote | None:
        """Aktuelle Kursdaten fuer eine Aktie abrufen."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info or not isinstance(info, dict):
                return None

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose")
            open_price = info.get("open")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")
            volume = info.get("volume")
            market_cap = info.get("marketCap")
            week52_high = info.get("fiftyTwoWeekHigh")
            week52_low = info.get("fiftyTwoWeekLow")
            regular_close = info.get("regularMarketPreviousClose")

            prev_close = previous_close or regular_close
            price_change_pct = None
            if prev_close and prev_close > 0 and current_price:
                price_change_pct = ((current_price - prev_close) / prev_close) * 100.0

            name = info.get("longName") or info.get("shortName") or symbol
            currency = info.get("currency") or "USD"

            return StockQuote(
                symbol=symbol.upper(),
                name=name or symbol,
                current_price=round(current_price, 2) if current_price else None,
                previous_close=round(prev_close, 2) if prev_close else None,
                open_price=round(open_price, 2) if open_price else None,
                day_high=round(day_high, 2) if day_high else None,
                day_low=round(day_low, 2) if day_low else None,
                price_change_pct=round(price_change_pct, 2) if price_change_pct else None,
                volume=volume,
                market_cap=market_cap,
                week52_high=round(week52_high, 2) if week52_high else None,
                week52_low=round(week52_low, 2) if week52_low else None,
                currency=currency,
            )
        except Exception as exc:
            logger.error("Fehler beim Abrufen von Kursdaten fuer %s: %s", symbol, exc)
            return None

    def fetch_chart(self, symbol: str, period: str = "1mo") -> StockChart:
        """Historische Kursdaten fuer ein Chart abrufen."""
        chart = StockChart(symbol=symbol, period=period)

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                return chart

            chart.dates = [
                d.strftime("%d.%m.%Y") for d in hist.index.to_pydatetime()
            ]
            chart.prices = [
                round(float(c), 2) for c in hist["Close"].dropna().values
            ]
        except Exception as exc:
            logger.error("Fehler beim Abrufen von Chart-Daten fuer %s: %s", symbol, exc)

        return chart
