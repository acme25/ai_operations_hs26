# Auftrag 2 – Azure Machine Learning

Prognose des stündlichen Verkehrsaufkommens auf der Interstate 94 in Minneapolis (USA) mit Azure AutoML – trainiert, als Online Endpoint bereitgestellt und über ein Jupyter Notebook per REST-API aufgerufen.

## Demo-Video

<video controls src="../medien/Traffic_Volume_Prediction_Demo_AnnaNikitaMueller.mp4" title="Traffic Volume Prediction – Demo"></video>

Falls das Video nicht angezeigt wird: [Video herunterladen](../medien/Traffic_Volume_Prediction_Demo_AnnaNikitaMueller.mp4)

## Inhalt

| Datei | Beschreibung |
|---|---|
| `traffic_prediction.ipynb` | Jupyter Notebook: Endpoint-Aufruf und Visualisierungen |
| `.env.example` | Vorlage für Endpoint-URL und API-Key |
| `../medien/Traffic_Volume_Prediction_Demo_AnnaNikitaMueller.mp4` | Video zur Umsetzung und Demonstration |
| `README.md` | Diese Dokumentation |

## Datensatz

- **Quelle:** «Metro Interstate Traffic Volume» (Hogue, 2019)
- **Umfang:** 48'204 Einträge, 02.10.2012 – 30.09.2018
- **Zielvariable:** `traffic_volume` – Anzahl Fahrzeuge pro Stunde
- **Eingangsmerkmale:** u. a. Wetterbedingungen, Temperatur, Niederschlag, Feiertage und Zeitangaben

## Vorgehen

### Datenaufbereitung und Modelltraining

Das Training führte ich mit AutoML (Task: Zeitreihenprognose) durch. Bis zum finalen Modell waren drei Läufe nötig:

| Lauf | Ergebnis | Erkenntnis |
|---|---|---|
| 1 | Fehler wegen doppelter Zeitstempel | Stündliche Frequenz mit Zielaggregation «Mittelwert» eingestellt |
| 2 | Nach 3 Stunden manuell abgebrochen | Timeout versehentlich auf 3'600 statt 360 Minuten gesetzt – entdeckt in «Alle Eigenschaften als JSON Rohdaten anzeigen» |
| 3 | Erfolgreich, rund 6 Stunden | Verschiedene Algorithmen, Prognosehorizont 24 Stunden |

**Gewähltes Modell:** LightGBM mit dem niedrigsten Fehler von **0.03719**. Das Modell habe ich registriert und als **Online Endpoint** bereitgestellt.

### Endpoint-Aufruf

Den Endpoint rufe ich im Notebook über die REST-API auf:

1. Historische Verkehrsdaten laden
2. Zielvariable `traffic_volume` entfernen
3. Zukünftige Zeitpunkte simulieren
4. Eingabedaten als JSON-Payload an den Endpoint senden

Endpoint-URL und API-Key werden aus einer lokalen `.env`-Datei geladen und sind nicht im Repository enthalten. Zum Ausführen `.env.example` nach `.env` kopieren und die eigenen Werte eintragen.

### Visualisierungen

Im Notebook erstelle ich drei Darstellungen:

- **Einzelstundenprognose**
- **Sieben Tage Historie** mit der folgenden Prognosestunde
- **Interaktives Plotly-Dashboard** mit 24 Stunden Historie und 24 stündlichen Prognosewerten

Das Dashboard ist bewusst als 48-Stunden-Ansicht gestaltet: Aus Sicht einer Führungskraft ist vor allem der Vergleich zwischen vergangenem und prognostiziertem Folgetag interessant – so lassen sich Verkehrsspitzen und ruhigere Zeiträume besser erkennen.

Den Code für die Visualisierungen habe ich nach mehreren eigenen Versuchen mit ChatGPT erstellt («Vibe Coding»). Darstellung und Inhalt – welche Zeiträume gezeigt werden und wie Historie und Prognose kombiniert werden – habe ich selbst vorgegeben.

## Kosten auf Azure

### Verursachte Kosten

Gemäss Azure Cost Management (Stand 23.10.2026) entstanden in meiner Ressourcengruppe:

| Position | Kosten |
|---|---|
| 21.10.2026 | CHF 5.81 |
| 22.10.2026 | CHF 1.89 |
| **Total** | **CHF 7.70** |

**Grösste Kostentreiber:**

| Dienst | Kosten |
|---|---|
| Azure Synapse Analytics | CHF 4.66 |
| Virtual Machines | CHF 2.39 |

Die Kosten entstanden vor allem durch die Rechenleistung für das AutoML-Training (mehrere Läufe, verschiedene Algorithmen, fünf Kreuzvalidierungen) sowie durch den Online Endpoint und die Notebook-Rechenumgebung.

### Optimierungspotenzial

- **Timeout korrekt setzen** – im zweiten Lauf 3'600 statt 360 Minuten
- **Modellversuche begrenzen** – maximal 1'000 Versuche waren für den kleinen Datensatz zu viel
- **Ergebnisse frühzeitig prüfen** – LightGBM war bereits nach zwei bis drei Stunden verfügbar, der Lauf dauerte aber rund sechs Stunden

### Vergleich On-Prem

Da der Datensatz klein ist und kein Deep Learning verwendet wird, würde ein leistungsfähiger PC mit genügend Arbeitsspeicher und guter CPU ausreichen. Bei vorhandener Hardware fallen vor allem Strom- und Zeitkosten für Einrichtung, Training und Wartung an; bei einer Neuanschaffung zusätzlich Hardwarekosten. API-Bereitstellung und Sicherheitsmassnahmen müsste ich selbst betreiben.

**Fazit:** Für ein einmaliges Studienprojekt ist Azure ML die bessere Wahl – keine eigene Infrastruktur, Bezahlung nur nach Nutzung. Bei regelmässigem Training und vorhandener Hardware könnte On-Prem langfristig günstiger sein, ist aber im Betrieb deutlich zeitaufwendiger.

## Hilfsmittel

| Hilfsmittel | Verwendung | Betroffene Dateien |
|---|---|---|
| ChatGPT | Generierung des Visualisierungscodes nach eigenen Vorgaben («Vibe Coding») | `traffic_prediction.ipynb` (Schritte 3–6) |
| Claude | Überarbeitung der Notebook-Texte und Umstellung auf `.env` für den API-Key | `traffic_prediction.ipynb` |
| Claude | Erstellung der README-Dokumentation auf Basis meines Berichts | `README.md` |