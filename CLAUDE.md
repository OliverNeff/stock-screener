# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Desktop-Aktienbeobachtungsanwendung (Python, customtkinter, yfinance, matplotlib).

## Struktur

```
src/stock_screener/
  main.py              -- Entry point (ruft App().run() auf)
  app.py               -- Hauptanwendung: Window-Management, Layout, Daten-Koordination
  models/
    stock.py           -- Dataclasses: StockQuote, StockChart, WatchlistItem
  services/
    yahoo_finance.py   -- YahooFinanceService: Suche, Kursdaten, Charts (yfinance)
  ui/
    theme.py           -- Farben, Schriftarten, Chart-Farben
    components/
      watchlist_panel.py   -- Linkes Panel: Aktienliste mit Suche/Filter
      detail_panel.py      -- Rechtes Panel: Kursdetails + matplotlib-Chart
      search_dialog.py     -- Modaler Dialog zur Aktiensuche (debounce)
  utils/
    __init__.py        -- format_currency, format_percentage, format_volume, format_market_cap, debounce
data/
  tickers.json         -- Eingebettete Liste US-amerikanischer Tickers (~600 Einträge)
tests/
  test_services.py     -- Tests fuer YahooFinanceService, Formatierungsfunktionen, Integrationstests
```

## Wichtige Befehle

```bash
# Abhängigkeiten installieren
pip install -e ".[dev]"

# Tests ausführen (alle außer Integrationstests)
pytest -m "not integration"

# Alle Tests (inkl. Integration)
pytest

# Anwendung starten
python -m stock_screener.main
```

## Architektur

- **App** (app.py) koordiniert alle Datenflüsse. Lädt/speichert die Watchlist JSON (`~/.stock_screener_watchlist.json`).
- **YahooFinanceService** kapselt alle yfinance-Aufrufe. Die eingebettete Ticker-Liste (`data/tickers.json`) dient der Offline-Suche.
- **UI** ist in Panels aufgeteilt: WatchlistPanel (links) und DetailPanel (rechts, mit matplotlib-Chart).
- Datenabrufe laufen asynchron in Threads; UI-Updates erfolgen via `root.after(0, ...)`.
- `utils/debounce` ist customtkinter-spezifisch und nutzt `root.after()` zur Verzögerung.
