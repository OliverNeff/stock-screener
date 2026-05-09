"""Theme-Konfiguration fuer die Anwendung."""

from __future__ import annotations

import customtkinter as ctk


def apply_theme() -> None:
    """Globales Dark-Theme aktivieren."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


# Farbtabelle
COLORS: dict[str, str] = {
    "bg": "#1B1B1B",
    "bg_secondary": "#2B2B2B",
    "fg": "#E0E0E0",
    "fg_secondary": "#A0A0A0",
    "accent": "#00D1FF",
    "positive": "#00E676",
    "negative": "#FF5252",
    "danger": "#C62828",
    "danger_hover": "#E53935",
    "border": "#3B3B3B",
    "chart_grid": "#3B3B3B",
    "chart_line": "#00D1FF",
    "chart_fill": "#00D1FF",
    "hover": "#3A3A3A",
}

# Schriftarten
FONTS: dict[str, tuple[str, int, str] | tuple[str, int]] = {
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 9),
    "large": ("Segoe UI", 28, "bold"),
    "medium": ("Segoe UI", 12),
    "period_button": ("Segoe UI", 10, "bold"),
}

CHART_COLORS = {
    "grid": COLORS["chart_grid"],
    "line": COLORS["chart_line"],
    "fill": COLORS["chart_fill"],
    "text": COLORS["fg"],
    "bg": COLORS["bg"],
}


def get_theme_colors() -> dict[str, str]:
    """Gibt die aktuelle Farbpalette zurueck."""
    return dict(COLORS)


def get_theme_fonts() -> dict[str, tuple[str, int, str] | tuple[str, int]]:
    """Gibt die aktuellen Schriftarten zurueck."""
    return dict(FONTS)
