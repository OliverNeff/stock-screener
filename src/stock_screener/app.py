"""Hauptanwendung: Window-Management, Layout und Daten-Koordination."""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any

import customtkinter as ctk

import tkinter as tk

from stock_screener.models.stock import StockChart, StockQuote, WatchlistItem
from stock_screener.services.yahoo_finance import YahooFinanceService
from stock_screener.ui.theme import apply_theme, COLORS
from stock_screener.ui.components.watchlist_panel import WatchlistPanel
from stock_screener.ui.components.detail_panel import DetailPanel
from stock_screener.ui.components.search_dialog import SearchDialog

logger = logging.getLogger(__name__)

# Speicherort der Watchlist
_WATCHLIST_PATH = Path.home() / ".stock_screener_watchlist.json"


class App:
    """Hauptanwendung der Aktienbeobachtung."""

    def __init__(self) -> None:
        apply_theme()

        self.root = ctk.CTk()
        self.root.title("Stock Screener")
        self.root.geometry("1100x650")
        self.root.minsize(800, 500)

        # DPI-Awareness
        if os.name == "nt":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        self.service = YahooFinanceService()
        self.service.refresh_ticker_list()

        self.watchlist: list[WatchlistItem] = self._load_watchlist()
        self.selected_symbol: str | None = None
        self.current_quote: StockQuote | None = None
        self._loading = False

        self._build_ui()

    def _build_ui(self) -> None:
        # Haupt-Container
        self._main_frame = ctk.CTkFrame(self.root, fg_color=COLORS["bg"])
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        # Watchlist-Panel (links)
        self._watchlist_panel = WatchlistPanel(
            self._main_frame,
            on_select=self._on_stock_select,
            on_search=self._on_show_search,
            on_refresh=self._on_refresh_all,
        )
        self._watchlist_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4), pady=4)

        # Detail-Panel (rechts)
        self._detail_panel = DetailPanel(
            self._main_frame,
            on_period_change=self._on_period_change,
        )
        self._detail_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0), pady=4)

        self._update_watchlist_display()

    def _update_watchlist_display(self) -> None:
        self._watchlist_panel.set_watchlist(self.watchlist)

    def _on_stock_select(self, symbol: str) -> None:
        """Aktie ausgewählt."""
        self.selected_symbol = symbol
        self._watchlist_panel.select_stock(symbol)
        self._fetch_data(symbol)

    def _on_show_search(self) -> None:
        """Such-Dialog anzeigen."""
        SearchDialog(self.root, self.service, self._on_add_to_watchlist)

    def _on_add_to_watchlist(self, symbol: str) -> None:
        """Aktie zur Watchlist hinzufügen."""
        # Nur das Symbol extrahieren (vor dem ersten " - " Trenner)
        symbol = symbol.strip().upper().split(" - ")[0].strip()
        if not symbol:
            return

        # Prüfen ob bereits in Watchlist
        if any(item.symbol == symbol for item in self.watchlist):
            # Symbol ist bereits in der Watchlist
            return

        name = self._get_stock_name(symbol)
        self.watchlist.append(WatchlistItem(
            symbol=symbol,
            display_name=f"{symbol}  -  {name}",
        ))
        self._save_watchlist()
        self._update_watchlist_display()
        self._on_stock_select(symbol)

    def _get_stock_name(self, symbol: str) -> str:
        """Firmenname ermitteln."""
        for item in self.watchlist:
            if item.symbol == symbol and item.display_name:
                parts = item.display_name.split(" - ")
                if len(parts) > 1:
                    return parts[1].strip()
        # Schneller Test via yfinance
        try:
            import yfinance as yf
            info = yf.Ticker(symbol).info
            if info and isinstance(info, dict):
                return info.get("longName") or info.get("shortName") or symbol
        except Exception:
            pass
        return symbol

    def _on_refresh_all(self) -> None:
        """Alle Kurse aktualisieren."""
        for item in self.watchlist:
            threading.Thread(
                target=self._fetch_quote_single,
                args=(item.symbol,),
                daemon=True,
            ).start()

    def _on_period_change(self, period: str) -> None:
        """Chart-Periode geändert."""
        if self.selected_symbol:
            self._fetch_chart(self.selected_symbol, period)

    def _fetch_data(self, symbol: str) -> None:
        """Kursdaten und Chart asynchron laden."""
        if self._loading:
            return
        self._loading = True
        self._detail_panel.show_placeholder()

        def _on_complete(quote: StockQuote | None, chart: StockChart) -> None:
            self._loading = False
            self.current_quote = quote
            if quote:
                self._watchlist_panel.update_quote(symbol, quote)
            self._detail_panel.update_quote(quote) if quote else None
            self._detail_panel.update_chart(chart)
            self._save_watchlist()  # Speichere Watchlist nach Datenaktualisierung

        def _fetch() -> tuple[StockQuote | None, StockChart]:
            quote = self.service.fetch_quote(symbol)
            chart = self.service.fetch_chart(symbol)
            self.root.after(0, lambda: _on_complete(quote, chart))
            return quote, chart

        threading.Thread(target=_fetch, daemon=True).start()

    def _fetch_quote_single(self, symbol: str) -> None:
        """Einen einzelnen Kurs aktualisieren."""
        quote = self.service.fetch_quote(symbol)
        if quote:
            self.root.after(0, lambda s=symbol: self._watchlist_panel.update_quote(s, quote))

    def _fetch_chart(self, symbol: str, period: str) -> None:
        """Chart asynchron aktualisieren."""
        if self._loading:
            return
        chart = self.service.fetch_chart(symbol, period)
        self.root.after(0, lambda: self._detail_panel.update_chart(chart))

    def _load_watchlist(self) -> list[WatchlistItem]:
        """Watchlist aus JSON laden."""
        try:
            with open(_WATCHLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [
                WatchlistItem(symbol=item["symbol"], display_name=item.get("display_name", ""))
                for item in data
            ]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_watchlist(self) -> None:
        """Watchlist in JSON speichern."""
        try:
            data = [
                {"symbol": item.symbol, "display_name": item.display_name}
                for item in self.watchlist
            ]
            _WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_WATCHLIST_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as exc:
            logger.warning("Watchlist konnte nicht gespeichert werden: %s", exc)

    def run(self) -> None:
        """Anwendung starten."""
        self.root.mainloop()
