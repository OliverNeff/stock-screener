"""Tests für YahooFinanceService und Utility-Functions."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from stock_screener.services.yahoo_finance import YahooFinanceService
from stock_screener.utils import format_currency, format_percentage, format_volume


logger = logging.getLogger(__name__)

# Fixtures
@pytest.fixture
def service() -> YahooFinanceService:
    svc = YahooFinanceService()
    svc.refresh_ticker_list()
    return svc


# --- Tests für YahooFinanceService ---

class TestYahooFinanceService:
    """Testen der YahooFinanceService-Klasse."""

    def test_search_returns_results(self, service: YahooFinanceService) -> None:
        """Die Suche sollte Ergebnisse für bekannte Ticker liefern."""
        results = service.search("AAPL")
        assert len(results) > 0
        assert any(r["symbol"] == "AAPL" for r in results)

    def test_search_by_name(self, service: YahooFinanceService) -> None:
        """Die Suche sollte auch nach Firmennamen funktionieren."""
        results = service.search("Microsoft")
        assert len(results) > 0
        assert any("MSFT" in r["symbol"] for r in results)

    def test_search_case_insensitive(self, service: YahooFinanceService) -> None:
        """Die Suche sollte case-insensitive sein."""
        results_lower = service.search("aapl")
        results_upper = service.search("AAPL")
        assert len(results_lower) == len(results_upper)

    @patch("stock_screener.services.yahoo_finance.yf.Ticker")
    def test_fetch_quote_valid_symbol(
        self, mock_ticker_cls: MagicMock, service: YahooFinanceService
    ) -> None:
        """Ein gültiges Symbol sollte einen StockQuote zurückliefern."""
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "currentPrice": 150.25,
            "regularMarketPreviousClose": 148.00,
            "open": 149.50,
            "dayHigh": 152.00,
            "dayLow": 147.00,
            "volume": 54_000_000,
            "marketCap": 2_500_000_000_000,
            "fiftyTwoWeekHigh": 180.00,
            "fiftyTwoWeekLow": 120.00,
            "longName": "Apple Inc.",
            "currency": "USD",
        }
        mock_ticker_cls.return_value = mock_ticker

        quote = service.fetch_quote("AAPL")

        assert quote is not None
        assert quote.symbol == "AAPL"
        assert quote.current_price == 150.25
        assert quote.price_change_pct == pytest.approx(1.52, abs=0.01)
        assert quote.volume == 54_000_000
        assert quote.market_cap == 2_500_000_000_000

    @patch("stock_screener.services.yahoo_finance.yf.Ticker")
    def test_fetch_quote_invalid_symbol(
        self, mock_ticker_cls: MagicMock, service: YahooFinanceService
    ) -> None:
        """Ein ungültiges Symbol sollte None zurückliefern."""
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        quote = service.fetch_quote("ZZZZZZ")

        assert quote is None

    @patch("stock_screener.services.yahoo_finance.yf.Ticker")
    def test_fetch_chart_valid_symbol(
        self, mock_ticker_cls: MagicMock, service: YahooFinanceService
    ) -> None:
        """Ein gültiges Symbol sollte Chart-Daten zurückliefern."""
        import pandas as pd

        mock_ticker = MagicMock()
        # Simuliere 5 Tage von Daten
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        prices = [100.0, 101.5, 102.0, 100.5, 103.0]
        hist = pd.DataFrame({"Close": prices}, index=dates)
        mock_ticker.history.return_value = hist
        mock_ticker_cls.return_value = mock_ticker

        chart = service.fetch_chart("AAPL", "5d")

        assert chart.symbol == "AAPL"
        assert len(chart.dates) == 5
        assert len(chart.prices) == 5
        assert chart.dates[0] == "01.01.2024"
        assert chart.prices[4] == 103.0

    @patch("stock_screener.services.yahoo_finance.yf.Ticker")
    def test_fetch_chart_empty(
        self, mock_ticker_cls: MagicMock, service: YahooFinanceService
    ) -> None:
        """Ein Symbol ohne Daten sollte ein leeres Chart zurückliefern."""
        mock_ticker = MagicMock()
        import pandas as pd
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        chart = service.fetch_chart("ZZZZZZ", "1mo")

        assert chart.symbol == "ZZZZZZ"
        assert len(chart.dates) == 0
        assert len(chart.prices) == 0

    def test_search_empty_query(self, service: YahooFinanceService) -> None:
        """Eine leere Suche sollte keine Ergebnisse liefern."""
        results = service.search("")
        assert results == []


# --- Tests für Utility-Functions ---

class TestFormatCurrency:
    """Testen der format_currency-Funktion."""

    def test_format_currency_valid(self) -> None:
        assert format_currency(1234.56) == "$1,234.56"

    def test_format_currency_negative(self) -> None:
        assert format_currency(-50.0) == "$-50.00"

    def test_format_currency_none(self) -> None:
        assert format_currency(None) == "N/A"

    def test_format_currency_eur(self) -> None:
        assert format_currency(99.9, "EUR") == "€99.90"


class TestFormatPercentage:
    """Testen der format_percentage-Funktion."""

    def test_format_positive(self) -> None:
        assert format_percentage(1.5) == "+1.50%"

    def test_format_negative(self) -> None:
        assert format_percentage(-0.5) == "-0.50%"

    def test_format_zero(self) -> None:
        assert format_percentage(0.0) == "0.00%"

    def test_format_none(self) -> None:
        assert format_percentage(None) == "N/A"


class TestFormatVolume:
    """Testen der format_volume-Funktion."""

    def test_format_k(self) -> None:
        assert format_volume(54_300) == "54.3K"

    def test_format_m(self) -> None:
        assert format_volume(1_234_567) == "1.2M"

    def test_format_none(self) -> None:
        assert format_volume(None) == "N/A"


# --- Integrationstests (benötigen Netzwerk) ---

@pytest.mark.integration
class TestIntegrationYahooFinance:
    """Integrationstests - benötigen Internetverbindung."""

    def test_real_fetch_quote(self, service: YahooFinanceService) -> None:
        """Test gegen echte Yahoo-Daten."""
        quote = service.fetch_quote("AAPL")
        assert quote is not None
        assert quote.current_price is not None
        assert quote.current_price > 0

    def test_real_fetch_chart(self, service: YahooFinanceService) -> None:
        """Test gegen echte Yahoo-Daten."""
        chart = service.fetch_chart("AAPL", "5d")
        assert chart.symbol == "AAPL"
        assert len(chart.dates) > 0
        assert len(chart.prices) > 0

    def test_real_search(self, service: YahooFinanceService) -> None:
        """Test der eingebetteten Suche."""
        results = service.search("Tesla")
        assert len(results) > 0
        assert any("TSLA" in r["symbol"] for r in results)
