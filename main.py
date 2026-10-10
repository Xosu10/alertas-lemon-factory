import logging
from datetime import datetime, timezone

from ciclo import comprobar
from discord_notifier import send_discord_message
from fetch import get_events
from storage import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("lemon_factory")


def main():
    init_db()
    logger.info("Comprobando el parte de la huerta...")

    try:
        comprobar(get_events(), datetime.now(timezone.utc), send_discord_message)
    except Exception:
        logger.exception("Error en esta comprobación. Se reintentará en la siguiente ejecución programada.")

    logger.info("Comprobación terminada.")


if __name__ == "__main__":
    main()
