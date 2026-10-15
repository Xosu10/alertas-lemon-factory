from collections import Counter
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config import FIRST_ALERT_MINUTES, SECOND_ALERT_MINUTES
from envio import enviar_una_vez
from messages import Tormenta, es_de_madrugada, primera_alerta, segunda_alerta

MADRID = ZoneInfo("Europe/Madrid")


def agrupar(eventos):
    """Une los eventos que salen exactamente a la misma hora y minuto en una sola tormenta."""
    cuantos = Counter(datetime.fromisoformat(e["date"]) for e in eventos)
    return [Tormenta(cuando.astimezone(MADRID), n) for cuando, n in sorted(cuantos.items())]


def tipo_de_alerta(minutos_restantes):
    """'primera' si quedan entre 30 y 60 min, 'segunda' si quedan 30 o menos, None si ya pasó o falta mucho."""
    if minutos_restantes <= 0:
        return None
    if minutos_restantes <= SECOND_ALERT_MINUTES:
        return "segunda"
    if minutos_restantes <= FIRST_ALERT_MINUTES:
        return "primera"
    return None


def clave(tormenta):
    """Identifica la tormenta por su instante exacto: si el calendario cambia la hora, es otra tormenta distinta."""
    return "tormenta|" + tormenta.cuando.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def enviar_alertas(eventos, ahora, enviar):
    """Envía la alerta que toque a cada tormenta, una sola vez. `enviar(texto)` entrega el mensaje."""
    for tormenta in agrupar(eventos):
        minutos = (tormenta.cuando - ahora).total_seconds() / 60
        tipo = tipo_de_alerta(minutos)
        if tipo is None:
            continue

        n = max(1, round(minutos))
        texto = primera_alerta(n, tormenta) if tipo == "primera" else segunda_alerta(n, tormenta.cantidad, es_de_madrugada(tormenta))
        enviar_una_vez(clave(tormenta), f"alerta_{tipo}", texto, enviar)
