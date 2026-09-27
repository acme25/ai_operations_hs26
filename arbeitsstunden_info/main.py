from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from . import classes as cs

app = FastAPI(title="Arbeitsstunden Info API", description="API for managing Arbeitsstunden information")


BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/arbeitszeitcheck", response_model=cs.Output)
def arbeitszeit_check(eingabe: cs.Input):
    try:
        return cs.berechne_arbeitszeit(eingabe)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

