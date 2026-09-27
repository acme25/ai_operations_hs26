# Arbeitszeit- & Lohnrechner

Eine kleine REST-API, die Arbeitszeit und Lohn für mehrere Arbeitgeber berechnet inklusive Wochenendzuschlag, optionalem Monats-Soll-Tracking und optionaler Berechnung der Sozialabzüge (AHV/IV/EO, ALV).

## Features

- Berechnung der Netto-Arbeitszeit inkl. Pausenabzug (auch über Mitternacht hinweg)
- Automatischer Wochenendzuschlag (125%), abgeleitet aus dem Datum
- Optionales Tracking: verbleibende Stunden bis zum Monats-Soll
- Optionale Berechnung von Brutto- zu Netto-Lohn (AHV/IV/EO, ALV)
- Einfache Web-Oberfläche zur manuellen Eingabe, inkl. JSON-Ansicht und Excel-Export (Kopieren als Tab-getrennte Zeile) -> (TODO: Muss noch automatisiert werden)

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows PowerShell
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Starten

```bash
uvicorn arbeitsstunden_info.main:app --reload
```

- Web-UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interaktive API-Doku (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Input-Felder:**

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `arbeitgeber` | string | ja | Name des Arbeitgebers (mind. 3 Zeichen) |
| `startzeit` | datetime (ISO 8601) | ja | Beginn der Schicht |
| `endzeit` | datetime (ISO 8601) | ja | Ende der Schicht (kann am Folgetag liegen, z. B. Nachtschicht) |
| `pausenzeit_total_minuten` | int | ja | Pausendauer in Minuten (≥ 0) |
| `stundenlohn_chf` | float | ja | Stundenlohn in CHF (> 0) |
| `monat_soll_stunden` | float | nein | Monats-Soll in Stunden (> 0); erfordert `bereits_geleistete_stunden` |
| `bereits_geleistete_stunden` | float | nein | Bereits geleistete Stunden diesen Monat (≥ 0) |
| `sozialabzuege_berechnen` | bool | nein (Default `false`) | Ob AHV/IV/EO- und ALV-Abzüge berechnet werden sollen |

**Output-Felder:**

| Feld | Typ | Beschreibung |
|---|---|---|
| `arbeitgeber` | string | wie im Input |
| `datum` | date | Datum der Schicht (aus `startzeit` abgeleitet) |
| `arbeitszeit_stunden` | float | Netto-Arbeitszeit in Stunden |
| `verbleibende_stunden_monat` | float \| null | Restliche Stunden bis Monats-Soll; `null`, wenn kein Soll angegeben |
| `brutto_verdienst_chf` | float | Verdienst inkl. Wochenendzuschlag, vor Abzügen |
| `ahv_iv_eo_abzug` | float \| null | AHV/IV/EO-Abzug in CHF; `null`, wenn nicht berechnet |
| `alv_abzug` | float \| null | ALV-Abzug in CHF; `null`, wenn nicht berechnet |
| `netto_verdienst_chf` | float \| null | Verdienst nach Abzügen; `null`, wenn nicht berechnet |

## Design-Entscheidungen

- **Nachtschicht:** `startzeit`/`endzeit` sind volle `datetime`-Werte (nicht nur Uhrzeit) – dadurch funktioniert die Berechnung automatisch korrekt über Mitternacht hinweg, ganz ohne Sonderfall-Logik.
- **Wochenendzuschlag:** wird aus dem Wochentag von `startzeit` abgeleitet, kein separates Ja/Nein-Feld nötig.
- **Zuschlagshöhe:** fixer Prozentsatz als Konstante, nicht pro Request einstellbar.
- **Sozialabzüge:** nur AHV/IV/EO und ALV, da diese landesweit einheitliche Prozentsätze haben. NBU (branchen-/stundenabhängig) und BVG (altersabhängig, jahresbasiert) wurden bewusst **nicht** implementiert, da sie sich nicht sinnvoll auf eine einzelne Schicht herunterrechnen lassen.
- **Rundung:** durchgehend 2 Nachkommastellen für Stunden und CHF.
- **Zustandslosigkeit:** Die API speichert nichts zwischen Anfragen – `bereits_geleistete_stunden` muss bei jedem Aufruf mitgegeben werden. Bewusste Design-Entscheidung, u. a. weil render.com im Free-Tier keinen persistenten Speicher bietet.

## Ideen für Erweiterungen

- Batch-Skript zum automatisierten Ausfüllen mehrerer Schichten aus einer CSV (Konzept besprochen, noch nicht Teil dieses Repos)
- Persistente Historie pro Arbeitgeber/Monat

## Hilfsmittelverzeichnis
| Hilfsmittel | Verwendung | Betroffene Stellen |
|---|---|---|
| Claude | Schritt-für-Schritt-Mentoring beim eigenständigen Programmieren: Code-Reviews, Fehleranalyse, Diskussion von Design-Entscheidungen | Business-Logik in `classes.py`, API-Anbindung in `main.py` |
| Claude | Vollständige Generierung der Web-Oberfläche (HTML/CSS/JS) nach eigenen Vorgaben ("Vibe Coding") | `index.html` |
| Claude | Erstellung der README-Dokumentation basierend auf eigenen Notizen und dem Projektverlauf | `README.md` |

## Deployment
TODO:
- [x]Lokal Auftrag erledigen
- []README Dokumentation erstellen
- []automatisiertes Ausfüllen des Stundenzettels
- []Cloud Auftrag erledigen
