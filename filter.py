from config import ALL_DAY_TITLES

# El calendario no marca los eventos "de todo el día": les inventa una hora. Algunos se reconocen por el nombre.
PALABRAS_SIN_HORA = ("election",)


def _es_tormenta(evento):
    return evento.get("country") == "USD" and evento.get("impact") == "High"


def _sin_hora_exacta(evento):
    """True si la hora que trae el calendario no es una publicación real: un minuto que no es múltiplo de 5
    (las publicaciones reales caen en múltiplos de 5) o un nombre de evento de todo el día."""
    minuto = int(evento["date"][14:16])
    titulo = evento.get("title", "").lower()
    palabras = PALABRAS_SIN_HORA + ALL_DAY_TITLES
    return minuto % 5 != 0 or any(palabra in titulo for palabra in palabras)


def filtrar_tormentas(eventos):
    """Tormentas con hora exacta: las que tienen alertas de 1 hora y 30 minutos."""
    return [e for e in eventos if _es_tormenta(e) and not _sin_hora_exacta(e)]


def filtrar_tormentas_sin_hora(eventos):
    """Tormentas de todo el día: no hay hora exacta, solo aparecen en los resúmenes."""
    return [e for e in eventos if _es_tormenta(e) and _sin_hora_exacta(e)]
