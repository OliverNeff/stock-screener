"""Hilfsfunktionen fuer Formatierung und Validierung."""

from __future__ import annotations

import functools
from typing import Any, Callable

import customtkinter as ctk


def set_frame_color(widget: ctk.CTkBaseClass, color: str) -> None:
    """Setzt die Hintergrundfarbe eines Widgets (Frame, Button, Toplevel)."""
    if isinstance(widget, ctk.CTkButton):
        widget.configure(bg_color=color)
    else:
        widget.configure(fg_color=color)


def format_currency(value: float | None, currency: str = "USD") -> str:
    """Einen Geldbetrag formatieren."""
    if value is None:
        return "N/A"
    symbol_map = {"USD": "$", "EUR": "€", "GBP": "£"}
    sign = symbol_map.get(currency, f"{currency} ")
    return f"{sign}{value:,.2f}"


def format_percentage(value: float | None) -> str:
    """Einen Prozentsatz formatieren."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_volume(value: int | None) -> str:
    """Ein Volumen in kompakter Schreibweise formatieren."""
    if value is None:
        return "N/A"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def format_market_cap(value: float | None) -> str:
    """Die Marktkapitalisierung formatieren."""
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}B"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    return f"{value:,.0f}"


def debounce(delay_ms: int = 300) -> Callable:
    """Decorator, der Funktionsaufrufe debouncet.

    Eine neue Invocation setzt den Timer zurueck.
    """

    def decorator(func: Callable) -> Callable:
        timer: list[Any] = []

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            if timer:
                timer[0].cancel()

            def call() -> None:
                func(*args, **kwargs)

            timer.clear()
            import customtkinter as ctk

            root = getattr(wrapper, "_root", None)
            if root:
                timer.append(root.after(delay_ms, call))
            else:
                call()

        return wrapper

    return decorator
