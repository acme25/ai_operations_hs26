from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from typing import Optional

# Konfiguration
LOHN_ZUSCHLAG = 1.25
AHV_IV_EO_SATZ = 0.053
ALV_SATZ = 0.011


class Input(BaseModel):
    arbeitgeber: str = Field(min_length=3)  # Minimum Zeichenlänge von 3
    startzeit: datetime
    endzeit: datetime
    pausenzeit_total_minuten: int = Field(
        ge=0
    )  # Pausenzeit muss grösser und gleich Null sein
    stundenlohn_chf: float = Field(gt=0)  # Stundenlohn muss grösser als 0 sein
    monat_soll_stunden: Optional[float] = Field(
        default=None, gt=0
    )  # Stundenlimite darf nicht kleiner al 0 sein
    bereits_geleistete_stunden: Optional[float] = Field(
        default=None, ge=0
    )  # Bereits geleistete Arbeitsstunden soll grösser oder gleich 0 sein
    sozialabzuege_berechnen: bool = False


# Unser JSON Output
class Output(BaseModel):
    arbeitgeber: str
    datum: date
    arbeitszeit_stunden: float
    verbleibende_stunden_monat: Optional[float] = None
    brutto_verdienst_chf: float
    ahv_iv_eo_abzug: Optional[float] = None
    alv_abzug: Optional[float] = None
    netto_verdienst_chf: Optional[float] = None


# Funktion zur Berechnung von Sozialabzügen mit den Prozentzahlen in der Konfiguration
def berechne_sozialbezuege(
    brutto: float,
) -> tuple[
    float, float, float
]:  # Wird als Tuple retourniert, damit ich es in berechne_arbeitszeit() ins Output einspeisen kann
    abzug_ahv_iv_eo = round((brutto * AHV_IV_EO_SATZ), 2)
    abzug_alv = round(brutto * ALV_SATZ, 2)
    netto = round((brutto - abzug_ahv_iv_eo - abzug_alv), 2)
    return abzug_ahv_iv_eo, abzug_alv, netto


# Unsere Hauptfunktion, die in main.py aufgerufen wrid
def berechne_arbeitszeit(daten: Input) -> Output:
    # 1. Prüfung: Startzeit darf nicht grösser als die Endzeit sein
    if daten.startzeit > daten.endzeit:
        raise ValueError("Die Startzeit darf nicht nach der Endzeit liegen.")
    # 2. Prüfung: Endzeit darf nicht gleich sein wie die Startzeit
    elif daten.startzeit == daten.endzeit:
        raise ValueError("Die Startzeit darf nicht gleich der Endzeit sein.")

    brutto_zeit = (
        daten.endzeit - daten.startzeit
    )  # Berechnen von Arbeitszeit ohne Pausenzeit
    pause = timedelta(
        minutes=daten.pausenzeit_total_minuten
    )  # Berechnen von Pausenzeit

    # 3. Prüfung: Pausenzeit darf nicht länger sein als die Schichtdauer
    if pause >= brutto_zeit:
        raise ValueError("Die Pausenzeit darf nicht länger sein als die Arbeitszeit.")

    # Eigentliche Arbeitszeit berechnen + aufrunden auf zwei Kommastellen
    zeit = brutto_zeit - pause
    zeit = round(zeit.total_seconds() / 3600, 2)

    # Hier Verdienst berechnen mit dem Stundenlohn
    betrag = round(zeit * daten.stundenlohn_chf, 2)

    # 4. Prüfung: Wenn es sich um en Wochenende handelt, wird der der "betrag" also Verdienst auf 25 % aufgeschlagen
    if daten.startzeit.weekday() >= 5:
        betrag = round(betrag * LOHN_ZUSCHLAG, 2)

    # 5. Prüfung: Wenn Nutzer Sozialabzüge berechnen will
    if daten.sozialabzuege_berechnen:
        abzug_ahv_iv_eo, abzug_alv, netto = berechne_sozialbezuege(betrag)
    else:
        abzug_ahv_iv_eo = abzug_alv = netto = None

    # 6. Prüfung: Wenn die monatlichen Sollstunden und die bereitsgeleisteten Stunden angegeben wurden
    if (
        daten.monat_soll_stunden is not None
        and daten.bereits_geleistete_stunden is not None
    ):

        # 6.1: Bereitsgeleistete Stunden dürfen nicht grösser sein als monatliche Sollstunden
        if daten.monat_soll_stunden < daten.bereits_geleistete_stunden:
            raise ValueError(
                "bereits_geleistete_stunden darf nicht grösser sein als monat_soll_stunden."
            )
        # 6.2: Bereitsgeleistete Stunden + Arbeitszeit darf nicht die monatliche Sollstunden überschreiten
        elif daten.monat_soll_stunden < daten.bereits_geleistete_stunden + zeit:
            raise ValueError(
                "Die Summe aus bereits_geleistete_stunden und der aktuellen Arbeitszeit darf nicht grösser sein als monat_soll_stunden."
            )

        # Wenn Prüfungen überstanden, werden die verbleibende Stunden berechnet
        verbleibende_stunden = round(
            daten.monat_soll_stunden - (daten.bereits_geleistete_stunden + zeit), 2
        )

    # 7. Prüfung: Bereitsgeleistete Stunden kann nicht leer sein, wenn die monatlichen Sollstunden angegeben wurden
    elif (
        daten.monat_soll_stunden is not None
        and daten.bereits_geleistete_stunden is None
    ):
        raise ValueError(
            "bereits_geleistete_stunden muss angegeben werden, wenn monat_soll_stunden angegeben ist."
        )
    # 8. Prüfung: Monatlichen Sollstunden dürfen nicht leer sein, wenn die bereitsgeleistete Stunden angegeben wurden
    elif (
        daten.monat_soll_stunden is None
        and daten.bereits_geleistete_stunden is not None
    ):
        raise ValueError(
            "monat_soll_stunden muss angegeben werden, wenn bereits_geleistete_stunden angegeben ist."
        )
    else:
        verbleibende_stunden = None

    # JSON Output wird übergeben
    return Output(
        arbeitgeber=daten.arbeitgeber,
        datum=daten.startzeit.date(),
        arbeitszeit_stunden=zeit,
        verbleibende_stunden_monat=verbleibende_stunden,
        brutto_verdienst_chf=betrag,
        ahv_iv_eo_abzug=abzug_ahv_iv_eo,
        alv_abzug=abzug_alv,
        netto_verdienst_chf=netto,
    )
