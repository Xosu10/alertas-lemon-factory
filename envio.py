import logging

from storage import is_notified, mark_notified

logger = logging.getLogger("lemon_factory")


def enviar_una_vez(clave, tipo, texto, enviar):
    """Envía el mensaje solo si no se envió ya y lo apunta en el registro solo si Discord lo acepta."""
    if is_notified(clave, tipo):
        return False

    try:
        enviar(texto)
    except Exception:
        logger.exception("No se pudo enviar %s (%s); se reintentará en la siguiente pasada", tipo, clave)
        return False

    mark_notified(clave, tipo)
    logger.info("Enviado: %s (%s)", tipo, clave)
    return True
