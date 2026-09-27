from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from typing import Optional

#Konfiguration
LOHN_ZUSCHLAG = 1.25
AHV_IV_EO_SATZ = 0.053
ALV_SATZ = 0.011


class Input(BaseModel):
    arbeitgeber: str = Field(min_length=3)
    startzeit: datetime
    endzeit: datetime
    pausenzeit_total_minuten: int = Field(ge=0)
    stundenlohn_chf: float = Field(gt=0)
    monat_soll_stunden: Optional[float] = Field(default=None, gt=0)
    bereits_geleistete_stunden: Optional[float] = Field(default=None, ge=0)
    sozialabzuege_berechnen: bool = False


class Output(BaseModel):
    arbeitgeber: str
    datum: date
    arbeitszeit_stunden: float
    verbleibende_stunden_monat: Optional[float] = None
    brutto_verdienst_chf: float
    ahv_iv_eo_abzug: Optional[float]=None
    alv_abzug: Optional[float]=None
    netto_verdienst_chf: Optional[float]= None


def berechne_sozialbezuege(brutto: float) -> tuple[float, float, float]:
    abzug_ahv_iv_eo= round((brutto*AHV_IV_EO_SATZ), 2)
    abzug_alv= round(brutto*ALV_SATZ, 2)
    netto= round((brutto - abzug_ahv_iv_eo - abzug_alv), 2)
    return abzug_ahv_iv_eo, abzug_alv, netto


def berechne_arbeitszeit(daten: Input) -> Output:
    if daten.startzeit > daten.endzeit:
        raise ValueError("Die Startzeit darf nicht nach der Endzeit liegen.")
    elif daten.startzeit == daten.endzeit:
        raise ValueError("Die Startzeit darf nicht gleich der Endzeit sein.")

    brutto_zeit = daten.endzeit - daten.startzeit
    pause= timedelta(minutes= daten.pausenzeit_total_minuten)

    if pause >= brutto_zeit:
        raise ValueError("Die Pausenzeit darf nicht länger sein als die Arbeitszeit.")

    zeit = brutto_zeit - pause  

    zeit = round(zeit.total_seconds() / 3600, 2)
    betrag = round(zeit * daten.stundenlohn_chf, 2)   

    if daten.startzeit.weekday() >= 5:
        betrag = round(betrag * LOHN_ZUSCHLAG, 2)    

    if daten.sozialabzuege_berechnen:
        abzug_ahv_iv_eo, abzug_alv, netto = berechne_sozialbezuege(betrag)
    else:
        abzug_ahv_iv_eo= abzug_alv=  netto= None

    if (
        daten.monat_soll_stunden is not None
        and daten.bereits_geleistete_stunden is not None
    ):

        if (
            daten.monat_soll_stunden < daten.bereits_geleistete_stunden):
            raise ValueError(
                "bereits_geleistete_stunden darf nicht grösser sein als monat_soll_stunden.")
        elif (
            daten.monat_soll_stunden < daten.bereits_geleistete_stunden + zeit
        ):
            raise ValueError(
                "Die Summe aus bereits_geleistete_stunden und der aktuellen Arbeitszeit darf nicht grösser sein als monat_soll_stunden."
            )

        verbleibende_stunden = round(
            daten.monat_soll_stunden - (daten.bereits_geleistete_stunden + zeit), 2
        )

    elif (
        daten.monat_soll_stunden is not None
        and daten.bereits_geleistete_stunden is None
    ):
        raise ValueError(
            "bereits_geleistete_stunden muss angegeben werden, wenn monat_soll_stunden angegeben ist."
        )
    elif (
        daten.monat_soll_stunden is None
        and daten.bereits_geleistete_stunden is not None
    ):
        raise ValueError(
            "monat_soll_stunden muss angegeben werden, wenn bereits_geleistete_stunden angegeben ist."
        )
    else:
        verbleibende_stunden = None


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


