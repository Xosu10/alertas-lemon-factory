from config import IGNORED_TITLES

# El calendario no marca los eventos "de todo el día": les inventa una hora. Algunos se reconocen por el nombre.
PALABRAS_IGNORADAS = ("election",)


def _sin_hora_real(evento):
    """True si la hora del evento no es una publicación real: 00:00 exactas, un minuto que no es múltiplo de 5
    (las publicaciones reales caen en múltiplos de 5) o un nombre de evento de todo el día."""
    hora = evento["date"][11:19]
    minuto = int(evento["date"][14:16])
    titulo = evento.get("title", "").lower()
    palabras = PALABRAS_IGNORADAS + IGNORED_TITLES
    return hora == "00:00:00" or minuto % 5 != 0 or any(palabra in titulo for palabra in palabras)


def filtrar_tormentas(eventos):
    """Se queda con los eventos de alto impacto del país que nos interesa y con una hora real."""
    return [
        e
        for e in eventos
        if e.get("country") == "USD" and e.get("impact") == "High" and not _sin_hora_real(e)
    ]
