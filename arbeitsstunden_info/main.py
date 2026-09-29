from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from . import classes as cs

# Ordner der index.html
BASE_DIR = Path(__file__).resolve().parent

# Definition der FAST-API App
app = FastAPI(
    title="Arbeitsstunden Info API",
    description="API for managing Arbeitsstunden information",
)


# Aufruf der UI (Startseite)
@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html")


# API Abruf für die eigentliche Arbeitszeit- sowie Lohnberechnung
@app.post("/arbeitszeitcheck", response_model=cs.Output)
def arbeitszeit_check(eingabe: cs.Input):
    try:
        return cs.berechne_arbeitszeit(
            eingabe
        )  # Funktion wird aufgerufen und auch wird Output returniert
    # Error Handling
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
