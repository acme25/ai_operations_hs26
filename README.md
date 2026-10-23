# ai_operations_hs26

Repository für die Assignments im Modul «AI Operations» (Business AI, FHNW).

## Branches

Ich arbeite wie in der Praxis üblich mit zwei festen Branches:

- `main` – stabiler, abgabebereiter Stand
- `dev` – Entwicklung und Tests

Ab Auftrag 1.2 (Cloud) erweitere ich diesen Workflow um kurzlebige Feature-Branches und orientiere mich dabei an folgendem Modell:

![Branching-Modell mit main, dev und Feature-Branches](medien/GitBranches.png)

- `autocomplete` – Feature-Branch für den CSV-/Excel-Export der Berechnungen (in `dev` gemerged)

So festige ich gleichzeitig meine Git-Kenntnisse im Terminal.


## Auftrag 1 – DevOps

Arbeitszeit- und Lohnrechner für mehrere Arbeitgeber, bereitgestellt als REST-API mit FastAPI – lokal sowie in der Cloud auf render.com.

- Webseite: https://ai-operations-hs26.onrender.com
- Details: [`arbeitsstunden_info/README.md`](./arbeitsstunden_info/README.md)

## Auftrag 2 – Azure Machine Learning

Prognose des stündlichen Verkehrsaufkommens auf der Interstate 94 mit Azure AutoML (LightGBM), bereitgestellt als Online Endpoint und abgefragt über ein Jupyter Notebook.

- Demo-Video: [`medien/Traffic_Volume_Prediction_Demo_AnnaNikitaMueller.mp4`](./medien/Traffic_Volume_Prediction_Demo_AnnaNikitaMueller.mp4)
- Details: [`azure_info/README.md`](./azure_info/README.md)

## Hilfsmittelverzeichnis

| Hilfsmittel | Verwendung |
|---|---|
| Claude | Mentoring beim eigenständigen Programmieren: Code-Reviews, Fehleranalyse, Diskussion von Design-Entscheidungen |
| Claude | Generierung der Web-Oberfläche nach eigenen Vorgaben («Vibe Coding») |
| Claude | Überarbeitung der Notebook-Texte und sichere Auslagerung des API-Keys in eine `.env`-Datei |
| Claude | Erstellung der README-Dokumentation auf Basis eigener Notizen über alle Aufträge |
| ChatGPT | Generierung von Datenvisualisierung im Auftrag 2 nach eigenen Vorgaben («Vibe Coding») |

Die betroffenen Dateien pro Auftrag sind im jeweiligen Unter-README aufgeführt.