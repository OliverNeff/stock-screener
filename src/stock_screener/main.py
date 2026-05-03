"""Entry point der Stock Screener Anwendung."""

from __future__ import annotations

import logging

from stock_screener.app import App

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Hauptfunktion."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
