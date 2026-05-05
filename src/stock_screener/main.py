"""Entry point der Stock Screener Anwendung."""

from __future__ import annotations

import logging

from stock_screener.app import App

logging.basicConfig(level=logging.INFO)


# Monkey-patch customtkinter, um AttributeError bei zerstorten Widgets zu verhindern
# (Bug in customtkinter: _canvas ist zerstert (tk窗口 destroyed), aber callbacks feuern trotzdem nach)
def _patch_customtkinter() -> None:
    import customtkinter.windows.widgets.ctk_frame as ctk_frame_mod
    import customtkinter.windows.widgets.core_widget_classes as ctk_base_mod

    orig_draw = ctk_frame_mod.CTkFrame._draw

    def _draw_safe(self, *args: object, **kwargs: object) -> None:
        canvas = getattr(self, "_canvas", None)
        if canvas is None:
            return
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
        return orig_draw(self, *args, **kwargs)

    ctk_frame_mod.CTkFrame._draw = _draw_safe

    orig_update = ctk_base_mod.CTkBaseClass._update_dimensions_event

    def _update_safe(self, *args: object, **kwargs: object) -> None:
        if getattr(self, "_draw", None) is None:
            return
        return orig_update(self, *args, **kwargs)

    ctk_base_mod.CTkBaseClass._update_dimensions_event = _update_safe


_patch_customtkinter()


def main() -> None:
    """Hauptfunktion."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
