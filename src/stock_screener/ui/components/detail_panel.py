"""Rechte Panel-Seite: Kursdetails und Chart."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from stock_screener.models.stock import StockChart, StockQuote
from stock_screener.utils import (
    format_currency,
    format_percentage,
    format_market_cap,
    format_volume,
    set_frame_color,
)
from stock_screener.ui.theme import COLORS, FONTS, CHART_COLORS


class DetailPanel(ctk.CTkFrame):
    """Detail-Panel mit Kursinfo und Chart."""

    def __init__(self, parent: ctk.CTk, on_period_change: Callable[[str], None]) -> None:
        super().__init__(parent, fg_color=COLORS["bg"])
        self._on_period_change = on_period_change
        self._selected_period: str = "1mo"

        self._figure = Figure(figsize=(7, 3.5), dpi=100)
        self._figure.set_facecolor(COLORS["bg"])
        self._axis = self._figure.add_subplot(111)
        self._axis.set_facecolor(COLORS["bg"])
        self._axis.grid(True, color=CHART_COLORS["grid"], linewidth=0.5)
        self._axis.tick_params(colors=CHART_COLORS["text"])

        self._canvas: FigureCanvasTkAgg | None = None
        self._current_symbol: str | None = None
        self._current_chart: StockChart | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Container für alles
        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self._content.pack(fill=tk.BOTH, expand=True, padx=4)

        # Chart-Bereich
        self._chart_frame = tk.Frame(self._content, bg=COLORS["bg"])
        self._chart_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))

        # Info-Bereich unter dem Chart
        self._info_frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        self._info_frame.pack(fill=tk.X, padx=0, pady=(4, 0))

        self._lbl_symbol = ctk.CTkLabel(
            self._info_frame, text="--", font=FONTS["heading"],
            text_color=COLORS["accent"],
        )
        self._lbl_symbol.pack(anchor=tk.W, padx=12, pady=(8, 0))

        self._lbl_price = ctk.CTkLabel(
            self._info_frame, text="--", font=FONTS["large"],
            text_color=COLORS["fg"],
        )
        self._lbl_price.pack(anchor=tk.W, padx=12)

        self._lbl_change = ctk.CTkLabel(
            self._info_frame, text="--", font=FONTS["heading"],
            text_color=COLORS["fg_secondary"],
        )
        self._lbl_change.pack(anchor=tk.W, padx=12)

        # Period-Buttons
        self._period_frame = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self._period_frame.pack(fill=tk.X, pady=(0, 0))
        self._period_buttons: list[ctk.CTkButton] = []
        self._build_period_buttons()

        self._info_grid = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self._info_grid.pack(fill=tk.X, padx=0, pady=(4, 8))

    def _build_period_buttons(self) -> None:
        periods = [("1T", "5d"), ("1W", "1wk"), ("1M", "1mo"), ("3M", "3mo"),
                    ("6M", "6mo"), ("1J", "1y"), ("5J", "2y"), ("MAX", "max")]

        for text, period in periods:
            btn = ctk.CTkButton(
                self._period_frame, text=text, width=40, height=26,
                font=FONTS["period_button"], fg_color=COLORS["bg_secondary"],
                hover_color=COLORS["hover"], text_color=COLORS["fg"],
                corner_radius=4,
            )
            btn.pack(side=tk.LEFT, padx=1)
            btn.configure(command=lambda p=period: self._set_period(p))
            self._period_buttons.append(btn)

        self._highlight_period_button()

    def _highlight_period_button(self) -> None:
        for btn in self._period_buttons:
            set_frame_color(btn, COLORS["bg_secondary"])

    def _set_period(self, period: str) -> None:
        """Periode ändern und Callback auslösen."""
        self._selected_period = period
        self._highlight_period_button()
        self._on_period_change(period)

    def update_quote(self, quote: StockQuote) -> None:
        """Kursdetails aktualisieren."""
        self._current_symbol = quote.symbol

        name_short = quote.name[:30] + ("..." if len(quote.name) > 30 else "")
        self._lbl_symbol.configure(text=f"{quote.symbol}  –  {name_short}")

        if quote.current_price is not None:
            color = COLORS["positive"] if quote.price_change_pct is not None and quote.price_change_pct >= 0 else COLORS["fg"]
            self._lbl_price.configure(text=format_currency(quote.current_price, quote.currency))
            self._lbl_price.configure(text_color=color)

        if quote.price_change_pct is not None:
            color = COLORS["positive"] if quote.price_change_pct >= 0 else COLORS["negative"]
            self._lbl_change.configure(text=format_percentage(quote.price_change_pct))
            self._lbl_change.configure(text_color=color)

        self._update_info_grid(quote)

    def _get_prev_close(self) -> float:
        """Vorheriger Schließungskurs (interner Hilfswert)."""
        if self._current_chart and self._current_chart.prices:
            return self._current_chart.prices[-1] if len(self._current_chart.prices) > 1 else 0
        return 0

    def _update_info_grid(self, quote: StockQuote) -> None:
        """Info-Grid mit Details aktualisieren."""
        for child in self._info_grid.winfo_children():
            child.destroy()

        info_items = [
            ("Volumen", format_volume(quote.volume)),
            ("Markt-Kap.", format_market_cap(quote.market_cap)),
            ("52-Woch Hoch", format_currency(quote.week52_high, quote.currency)),
            ("52-Woch Tief", format_currency(quote.week52_low, quote.currency)),
            ("Eröffnung", format_currency(quote.open_price, quote.currency)),
            ("Tag Hoch", format_currency(quote.day_high, quote.currency)),
            ("Tag Tief", format_currency(quote.day_low, quote.currency)),
        ]

        for i, (label, value) in enumerate(info_items):
            col = i % 4
            row = i // 4

            lbl = ctk.CTkLabel(
                self._info_grid, text=label, font=FONTS["small"],
                text_color=COLORS["fg_secondary"],
            )
            lbl.grid(row=row, column=col, padx=(4, 0), pady=2, sticky=tk.W)

            val = ctk.CTkLabel(
                self._info_grid, text=value, font=FONTS["small"],
                text_color=COLORS["fg"],
            )
            val.grid(row=row, column=col + 1, pady=2, sticky=tk.E)

    def update_chart(self, chart: StockChart) -> None:
        """Chart aktualisieren."""
        self._current_chart = chart

        self._axis.clear()
        self._axis.set_facecolor(COLORS["bg"])
        self._figure.set_facecolor(COLORS["bg"])
        self._axis.grid(True, color=CHART_COLORS["grid"], linewidth=0.5)
        self._axis.tick_params(colors=CHART_COLORS["text"])

        if chart.prices and len(chart.prices) > 1:
            is_positive = chart.prices[-1] >= chart.prices[0] if chart.prices[0] else True
            line_color = COLORS["positive"] if is_positive else COLORS["negative"]
            fill_color = COLORS["positive"] if is_positive else COLORS["negative"]

            self._axis.plot(
                chart.dates, chart.prices, color=line_color,
                linewidth=1.5, alpha=0.9,
            )
            self._axis.fill_between(
                chart.dates, chart.prices, alpha=0.08, color=fill_color,
            )

            # Preis-Label
            last_price = chart.prices[-1]
            self._axis.annotate(
                f"${last_price:.2f}",
                xy=(chart.dates[-1], last_price),
                xytext=(5, -10),
                textcoords="offset points",
                fontsize=10,
                color=line_color,
                fontweight="bold",
            )

        self._axis.set_ylabel("Preis ($)", fontsize=9, color=CHART_COLORS["text"])
        self._axis.tick_params(axis="both", which="major", labelsize=8)

        # Titel
        if self._current_symbol:
            self._axis.set_title(
                f"{self._current_symbol}  –  {chart.period}",
                fontsize=10, color=CHART_COLORS["text"], pad=8,
            )

        self._figure.tight_layout()

        # Canvas neu erstellen
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._chart_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.draw_idle()

    def show_placeholder(self) -> None:
        """Leeren Zustand anzeigen."""
        self._current_symbol = None
        self._current_chart = None

        self._lbl_symbol.configure(text="Wähle eine Aktie")
        self._lbl_price.configure(text="--")
        self._lbl_change.configure(text="--")

        self._axis.clear()
        self._axis.set_facecolor(COLORS["bg"])
        self._figure.set_facecolor(COLORS["bg"])
        self._axis.text(0.5, 0.5, "Keine Aktie ausgewählt",
                        ha="center", va="center", fontsize=14,
                        color=COLORS["fg_secondary"])
        self._figure.tight_layout()

        if self._canvas:
            self._canvas.get_tk_widget().destroy()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._chart_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.draw_idle()
