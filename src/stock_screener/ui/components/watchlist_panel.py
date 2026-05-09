"""Linke Panel-Seite: Watchlist mit Aktienliste."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk

from stock_screener.models.stock import StockQuote, WatchlistItem
from stock_screener.utils import format_currency, format_percentage, set_frame_color
from stock_screener.ui.theme import COLORS, FONTS


class WatchlistPanel(ctk.CTkFrame):
    """Watchlist-Panel mit Aktienliste."""

    def __init__(
        self,
        parent: ctk.CTk,
        on_select: Callable[[str], None],
        on_search: Callable[[], None],
        on_refresh: Callable[[], None],
        on_delete: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent, fg_color=COLORS["bg_secondary"])
        self._on_select = on_select
        self._on_search = on_search
        self._on_refresh = on_refresh
        self._on_delete_callback = on_delete
        self._items: dict[str, ctk.CTkFrame] = {}
        self._selected_symbol: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Kopfzeile
        frm_header = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        frm_header.pack(fill=tk.X, padx=0, pady=(0, 0))

        lbl_title = ctk.CTkLabel(
            frm_header, text="Watchlist", font=FONTS["heading"],
            text_color=COLORS["accent"], anchor=tk.W,
        )
        lbl_title.pack(side=tk.LEFT, padx=12, pady=10)

        btn_refresh = ctk.CTkButton(
            frm_header, text="↻", width=36, height=28,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["bg_secondary"], hover_color=COLORS["hover"],
            text_color=COLORS["fg"],
        )
        btn_refresh.pack(side=tk.RIGHT, padx=4)
        btn_refresh.configure(command=self._on_refresh)

        btn_delete = ctk.CTkButton(
            frm_header, text="−", width=36, height=28,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["bg_secondary"], hover_color=COLORS["danger_hover"],
            text_color=COLORS["fg"],
            state=tk.DISABLED,
        )
        btn_delete.pack(side=tk.RIGHT, padx=4)
        btn_delete.configure(command=self._on_delete)
        self._btn_delete = btn_delete

        # Suche
        frm_search = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        frm_search.pack(fill=tk.X, padx=0, pady=(0, 4))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_text_changed)

        btn_search = ctk.CTkButton(
            frm_search, text="+ Aktie suchen", height=32,
            fg_color=COLORS["accent"], hover_color="#00A8CC",
            font=FONTS["medium"],
            command=self._on_search,
        )
        btn_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)

        # Scrollable Liste
        self._scrollable = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_secondary"])
        self._scrollable.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))

    def _on_search_text_changed(self, *_args: object) -> None:
        """Suchtext filtert die Watchlist dynamisch."""
        query = self._search_var.get().strip().upper()
        for symbol, widget in self._items.items():
            name = getattr(widget, "_display_name", "").upper()
            show = not query or query in symbol or query in name
            widget.pack_forget()
            widget.pack(fill=tk.X, padx=8, pady=2) if show else None

    def set_watchlist(self, items: list[WatchlistItem]) -> None:
        """Watchlist aktualisieren."""
        # Alte Elemente entfernen
        for widget in self._scrollable.winfo_children():
            widget.destroy()
        self._items.clear()

        for item in items:
            widget = self._create_item(item)
            self._items[item.symbol] = widget

    def select_stock(self, symbol: str) -> None:
        """Aktive Aktie hervorheben."""
        # Alte Auswahl aufheben
        for sym, widget in self._items.items():
            set_frame_color(widget, COLORS["bg_secondary"])

        # Neue Auswahl
        widget = self._items.get(symbol)
        if widget:
            set_frame_color(widget, COLORS["bg"])
            self._selected_symbol = symbol
            self._btn_delete.configure(state=tk.NORMAL)
            self._btn_delete.configure(text_color=COLORS["danger"])
        else:
            self._btn_delete.configure(state=tk.DISABLED)
            self._btn_delete.configure(text_color=COLORS["fg"])

    def delete_stock(self, symbol: str) -> None:
        """Aktie aus der Watchlist entfernen."""
        widget = self._items.pop(symbol, None)
        if widget:
            widget.destroy()
        if self._selected_symbol == symbol:
            self._selected_symbol = None
            self._btn_delete.configure(state=tk.DISABLED)
            self._btn_delete.configure(text_color=COLORS["fg"])

    def _on_delete(self) -> None:
        """Löschen-Callback."""
        if self._selected_symbol and self._on_delete_callback:
            self._on_delete_callback()

    def update_quote(self, symbol: str, quote: StockQuote) -> None:
        """Kursdaten für einen Watchlist-Eintrag aktualisieren."""
        widget = self._items.get(symbol)
        if not widget:
            return

        labels = widget.winfo_children()
        if len(labels) >= 3:
            lbl_price = labels[-2]
            lbl_change = labels[-1]

            if quote.current_price is not None:
                lbl_price.configure(text=format_currency(quote.current_price))

            if quote.price_change_pct is not None:
                color = COLORS["positive"] if quote.price_change_pct >= 0 else COLORS["negative"]
                lbl_change.configure(text=format_percentage(quote.price_change_pct))
                lbl_change.configure(text_color=color)

    def _create_item(self, item: WatchlistItem) -> ctk.CTkFrame:
        """Erstellt einen Watchlist-Eintrag."""
        frame = ctk.CTkFrame(self._scrollable, fg_color=COLORS["bg_secondary"], height=52)
        frame.pack(fill=tk.X, padx=8, pady=2)
        frame._display_name = item.display_name
        frame.configure(height=52)

        lbl_symbol = ctk.CTkLabel(
            frame, text=item.symbol, font=("Segoe UI", 12, "bold"),
            text_color=COLORS["fg"], width=60, anchor=tk.W,
        )
        lbl_symbol.pack(side=tk.LEFT, padx=(8, 4), fill=tk.Y)

        lbl_name = ctk.CTkLabel(
            frame, text=item.display_name[:25] + ("..." if len(item.display_name) > 25 else ""),
            font=FONTS["small"], text_color=COLORS["fg_secondary"],
            anchor=tk.W,
        )
        lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        lbl_price = ctk.CTkLabel(
            frame, text="--", font=("Segoe UI", 11, "bold"),
            text_color=COLORS["fg"], width=70, anchor=tk.E,
        )
        lbl_price.pack(side=tk.RIGHT, padx=4)

        lbl_change = ctk.CTkLabel(
            frame, text="--", font=("Segoe UI", 10),
            text_color=COLORS["fg_secondary"], width=60, anchor=tk.E,
        )
        lbl_change.pack(side=tk.RIGHT, padx=(0, 8))

        frame.bind("<Button-1>", lambda e, s=item.symbol: self._on_select(s))
        return frame

    def _on_search(self, *_args: object) -> None:
        """Such-Callback."""
        self._on_search()
