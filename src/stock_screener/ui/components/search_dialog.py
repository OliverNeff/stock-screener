"""Modaler Such-Dialog zum Hinzufügen von Aktien."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk

from stock_screener.services.yahoo_finance import YahooFinanceService
from stock_screener.utils import debounce, set_frame_color
from stock_screener.ui.theme import COLORS, FONTS


class SearchDialog(ctk.CTkToplevel):
    """Modaler Dialog zur Aktiensuche."""

    def __init__(
        self,
        parent: ctk.CTk,
        service: YahooFinanceService,
        on_add: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self.title("Aktie hinzufügen")
        self.geometry("400x300")
        self.resizable(False, False)

        self._service = service
        self._on_add = on_add
        self._results: list[dict[str, str]] = []

        # Modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        set_frame_color(self, COLORS["bg"])

        frm_search = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        frm_search.pack(fill=tk.X, padx=12, pady=(12, 0))

        self._entry = ctk.CTkEntry(frm_search, placeholder_text="Symbol oder Name eingeben...")
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4), pady=8)
        self._entry.focus_set()

        btn = ctk.CTkButton(frm_search, text="Hinzufügen", width=70,
                            fg_color=COLORS["accent"], hover_color="#00A8CC")
        btn.pack(side=tk.RIGHT, padx=4, pady=6)
        btn.bind("<Button-1>", self._on_add_clicked)

        # Ergebnisse-Liste
        self._listbox = ctk.CTkTextbox(self, height=200, fg_color=COLORS["bg_secondary"])
        self._listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 0))
        self._listbox.bind("<Double-Button-1>", self._on_item_doubleclick)

        self._entry.bind("<KeyRelease>", self._on_search)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    @debounce(300)
    def _do_search(self) -> None:
        query = self._entry.get().strip()
        self._results = self._service.search(query)
        self._render_results()

    def _on_search(self, _event: tk.Event | None = None) -> None:
        self._do_search()

    def _render_results(self) -> None:
        self._listbox.delete("1.0", tk.END)
        for item in self._results:
            self._listbox.insert(tk.END, f"{item['symbol']}  -  {item['name']}")

    def _on_item_doubleclick(self, event: tk.Event) -> None:
        idx_str = self._listbox.index(tk.INSERT)
        try:
            cursor = int(idx_str)
        except (ValueError, TypeError):
            return
        if 0 <= cursor < len(self._results):
            symbol = self._results[cursor]["symbol"]
            self.destroy()
            self._on_add(symbol)

    def _on_add_clicked(self, _event: tk.Event | None = None) -> None:
        """Sucheingabe als Symbol hinzufügen."""
        query = self._entry.get().strip().upper()
        if query:
            self.destroy()
            self._on_add(query)
