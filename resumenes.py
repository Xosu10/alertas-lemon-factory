import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import SUMMARY_HOUR
from envio import enviar_una_vez
from messages import resumen_diario, resumen_semanal
from tormentas import agrupar

MADRID = ZoneInfo("Europe/Madrid")
LUNES = 0
SABADO = 5
logger = logging.getLogger("lemon_factory")


def _fecha_madrid(evento):
    return datetime.fromisoformat(evento["date"]).astimezone(MADRID).date()


def _trae_la_semana(todos, lunes):
    """True si el calendario ya incluye algún evento (del tipo que sea) de la semana que empieza ese lunes."""
    domingo = lunes + timedelta(days=6)
    return any(lunes <= _fecha_madrid(e) <= domingo for e in todos)


def enviar_resumen_diario(todos, tormentas_filtradas, ahora, enviar):
    """De lunes a viernes, a partir de la hora del resumen, una vez al día, con las tormentas del día en curso (hora de España)."""
    ahora_madrid = ahora.astimezone(MADRID)
    if ahora_madrid.weekday() >= SABADO or ahora_madrid.hour < SUMMARY_HOUR:
        return

    hoy = ahora_madrid.date()
    if ahora_madrid.weekday() == LUNES and not _trae_la_semana(todos, hoy):
        logger.info("El calendario aún no trae la semana nueva; el resumen diario espera")
        return

    de_hoy = [e for e in tormentas_filtradas if _fecha_madrid(e) == hoy]
    texto = resumen_diario(ahora_madrid, agrupar(de_hoy))
    enviar_una_vez(f"dia|{hoy.isoformat()}", "resumen_diario", texto, enviar)


def enviar_resumen_semanal(todos, tormentas_filtradas, ahora, enviar):
    """Los lunes a partir de la hora del resumen, una vez por semana (lunes a domingo, hora de España)."""
    ahora_madrid = ahora.astimezone(MADRID)
    if ahora_madrid.weekday() != LUNES or ahora_madrid.hour < SUMMARY_HOUR:
        return

    lunes = ahora_madrid.date()
    if not _trae_la_semana(todos, lunes):
        logger.info("El calendario aún no trae la semana nueva; el resumen semanal espera")
        return

    domingo = lunes + timedelta(days=6)
    de_la_semana = [e for e in tormentas_filtradas if lunes <= _fecha_madrid(e) <= domingo]
    anio, semana, _ = ahora_madrid.isocalendar()
    texto = resumen_semanal(agrupar(de_la_semana))
    enviar_una_vez(f"semana|{anio}-W{semana:02d}", "resumen_semanal", texto, enviar)
