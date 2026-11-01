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
- **Merkmale:** u. a. Temperatur und Zeitangaben

## Vorgehen

### Datenaufbereitung und Modelltraining

Für das AutoML-Training (Task: Zeitreihenprognose) benötigte ich drei Versuche:

| Versuch | Ergebnis | Erkenntnis |
|---|---|---|
| 1 | Fehler wegen doppelter Zeitstempel | Behoben mit Frequenz «Stündlich» und Zielaggregation «Mittelwert» |
| 2 | Nach rund 3 Stunden manuell abgebrochen | Experiment-Timeout falsch eingestellt (3'600 statt 360 Minuten) |
| 3 | Erfolgreich, rund 6 Stunden | Prognosehorizont 24 Stunden |

**Gewähltes Modell:** LightGBM mit einem **normalisierten RMSE von 0.03719**. Das Modell habe ich registriert und als **Online Endpoint** bereitgestellt.

Der normalisierte RMSE beschreibt die Stärke der Vorhersagefehler. Beispielsweise könnte das Modell 5'000 Fahrzeuge prognostizieren, obwohl nur 4'800 Fahrzeuge unterwegs sind. Da der RMSE normalisiert ist, lässt sich aus dem Wert 0.03719 allein nicht ableiten, wie viele Fahrzeuge pro Stunde zu viel oder zu wenig prognostiziert wurden (Microsoft, o.D.).

### Endpoint-Aufruf

Den Endpoint rufe ich im Notebook über die REST-API auf:

1. Verkehrsdaten laden
2. Zielvariable `traffic_volume` entfernen
3. Eingabedaten als JSON-Payload an den Endpoint senden

> **Hinweis:** Für den Aufruf verwendete ich dieselben Daten wie für das Training. In der Praxis wären separate Testdaten geeigneter. Der Fokus lag hier auf dem technischen Nachweis des funktionierenden Endpoint-Aufrufs.

Endpoint-URL und API-Key werden aus einer lokalen `.env`-Datei geladen und sind nicht im Repository enthalten. Zum Ausführen `.env.example` nach `.env` kopieren und die eigenen Werte eintragen.

### Visualisierungen

Im Notebook erstelle ich drei Darstellungen:

- **Einzelstundenprognose**
- **Sieben Tage Historie** mit der folgenden Prognosestunde
- **Interaktives Plotly-Dashboard** mit 24 Stunden Historie und Prognosewerten für die nächsten 24 Stunden

Das Dashboard ist bewusst als 48-Stunden-Ansicht gestaltet: Aus Sicht einer Führungskraft ist vor allem der Vergleich zwischen vergangenem und prognostiziertem Folgetag interessant – so lassen sich mögliche Verkehrsspitzen und ruhigere Zeiträume besser erkennen.

Den Code für die Visualisierungen habe ich nach mehreren eigenen Versuchen mit ChatGPT erstellt («Vibe Coding»). Darstellung und Inhalt – welche Zeiträume gezeigt werden und wie Historie und Prognose kombiniert werden – habe ich selbst vorgegeben.

## Kosten auf Azure

### Verursachte Kosten

Gemäss Azure Cost Management (Stand 23.10.2026) entstanden in meiner Ressourcengruppe Gesamtkosten von **CHF 7.70** – und damit weniger als die erwarteten CHF 10.

| Datum | Kosten |
|---|---|
| 21.10.2026 | CHF 5.81 |
| 22.10.2026 | CHF 1.89 |
| **Total** | **CHF 7.70** |

**Grösste Kostentreiber:**

| Dienst | Kosten |
|---|---|
| Azure Synapse Analytics | CHF 4.66 |
| Virtual Machines | CHF 2.39 |

Die Kosten stehen vermutlich im Zusammenhang mit der benötigten Rechenleistung und Datenverarbeitung, insbesondere mit den mehrfachen AutoML-Trainingsläufen mit 5-facher Kreuzvalidierung. Die genauen Ursachen lassen sich aus der Kostenübersicht nicht eindeutig bestimmen.

### Optimierungspotenzial

- **Trainingszeit begrenzen** – im zweiten Versuch war der Timeout versehentlich auf 3'600 statt 360 Minuten gesetzt
- **Modellversuche begrenzen** – maximal 1'000 Versuche waren für den kleinen Datensatz vermutlich zu viel
- **Weniger Kreuzvalidierung** und **Einschränkung der getesteten Algorithmen**
- **Ergebnisse frühzeitig prüfen** – LightGBM war bereits nach zwei bis drei Stunden verfügbar, der Lauf dauerte aber rund sechs Stunden

Den Online Endpoint habe ich direkt nach der Aufnahme der Screenvideos gelöscht, um weitere Kosten zu vermeiden.

### Vergleich On-Prem

Da der Datensatz mit rund 48'000 Einträgen eher klein ist und kein Deep Learning verwendet wird, würde ein leistungsfähiger PC mit genügend Arbeitsspeicher und guter CPU ausreichen. Bei vorhandener Hardware fallen vor allem Stromkosten sowie Zeitaufwand für Einrichtung, Training und Wartung an; bei einer Neuanschaffung zusätzlich Hardwarekosten.

Bei einem kommerziellen Angebot kämen **Cybersecurity und Ausfallsicherheit** als weitere Kostenfaktoren hinzu:

- Schutzmassnahmen wie Firewalls, Zugriffskontrollen, Datensicherheit und Ersatzhardware
- Schutz vor manipulierten Eingabedaten (Data Poisoning), die zu falschen Prognosen führen könnten
- Eigene Absicherung und Verfügbarkeit der API
- Mögliche Folgekosten und Vertrauensverlust bei Sicherheitsvorfällen oder Systemausfällen

**Fazit:** Für ein einmaliges Studienprojekt ist Azure ML die bessere Wahl – keine eigene Infrastruktur, Bezahlung nur nach Nutzung. Bei regelmässiger Nutzung und bereits vorhandener Hardware könnte eine lokale Umsetzung langfristig kostengünstiger sein.

## Quellen

- Hogue, J. (05. Juni 2019). *Metro Interstate Traffic Volume*. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume
- Microsoft (o.D.). *Auswerten der Ergebnisse von AutoML-Experimenten*. Microsoft Learn. https://learn.microsoft.com/de-de/azure/machine-learning/how-to-understand-automated-ml

## Hilfsmittel

| Hilfsmittel | Verwendung | Betroffene Dateien |
|---|---|---|
| ChatGPT | Generierung des Visualisierungscodes nach eigenen Vorgaben («Vibe Coding») | `traffic_prediction.ipynb` (Schritte 3–6) |
| Claude | Überarbeitung der Notebook-Texte | `traffic_prediction.ipynb` |
| Claude | Erstellung der README-Dokumentation auf Basis meines Berichts | `README.md` |
