# stock-screener

Desktop-Aktienbeobachtungsanwendung mit Python, customtkinter und yfinance.

## Funktionen

- **Watchlist**: Verfolge deine Lieblingsaktien in einer persönlichen Liste
- **Live-Kursdaten**: Aktuelle Preise, Volumen, Marktkapitalisierung und mehr
- **Interaktive Charts**: Historische Kursverläufe mit wählbaren Zeiträumen
- **Offline-Suche**: ~600 US-Aktien sind eingebettet für die Suche ohne Internet
- **Persistente Speicherung**: Watchlist wird automatisch in `~/.stock_screener_watchlist.json` gespeichert
- **Dark Theme**: Augenschonendes Design für lange Beobachtungssessions

## Screenshot

![Stock Screener](docs/screenshot.png)

## Installation

### Voraussetzungen

- Python >= 3.10

### Einrichtung

```bash
# Virtual environment erstellen (empfohlen)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Abhängigkeiten installieren
pip install -e ".[dev]"
```

## Verwendung

```bash
# Anwendung starten
python -m stock_screener.main
```

### Bedienung

1. **Aktie hinzufügen**: Klicke auf "Aktie hinzufügen" und suche nach einem Ticker-Symbol oder Firmennamen
2. **Watchlist verwalten**: Klicke auf eine Aktie in der linken Liste, um Details zu sehen. Rechtsklick zum Entfernen.
3. **Kurse aktualisieren**: Klicke auf den "Aktualisieren"-Button, um alle Kurse zu frischen
4. **Chart ändern**: Wähle oben im Detailbereich einen Zeitraum (1W, 1Mo, 3Mo, 6Mo, 1Y, 5Y)

## Projektstruktur

```
src/stock_screener/
  main.py              -- Einstiegspunkt
  app.py               -- Hauptanwendung: Fenster, Layout, Daten-Management
  models/
    stock.py           -- Datenklassen: StockQuote, StockChart, WatchlistItem
  services/
    yahoo_finance.py   -- YahooFinanceService: Kurse, Charts, Suche (yfinance)
  ui/
    theme.py           -- Farben, Schriftarten, Chart-Stile
    components/
      watchlist_panel.py   -- Linkes Panel: Aktienliste mit Suche/Filter
      detail_panel.py      -- Rechtes Panel: Kursdetails + matplotlib-Chart
      search_dialog.py     -- Modaler Suchdialog mit Debounce
  utils/
    __init__.py        -- Formatierungsfunktionen, debounce
data/
  tickers.json         -- Eingebettete Ticker-Liste (~600 US-Aktien)
tests/
  test_services.py     -- Unit- und Integrationstests
```

## Architektur

- **App** ([app.py](src/stock_screener/app.py)) koordiniert alle Datenflüsse und UI-Updates
- **YahooFinanceService** ([yahoo_finance.py](src/stock_screener/services/yahoo_finance.py)) kapselt alle yfinance-Aufrufe
- **UI** ist in Panels aufgeteilt: WatchlistPanel (links) und DetailPanel (rechts)
- Datenabrufe laufen asynchron in Threads; UI-Updates erfolgen via `root.after(0, ...)`
- Die Ticker-Suche nutzt eine lokale JSON-Datei für Offline-Funktionalität

## Tests

```bash
# Alle Tests außer Integrationstests
pytest -m "not integration"

# Alle Tests (inkl. Integration)
pytest
```

## Konfiguration

Die Watchlist wird automatisch im Home-Verzeichnis gespeichert:

| Datei | Zweck |
| --- | --- |
| `~/.stock_screener_watchlist.json` | Gespeicherte Watchlist |