import os

from dotenv import load_dotenv

load_dotenv()


def _int_env(name, default):
    value = os.environ.get(name, "")
    return int(value) if value else default


DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# Minutos que faltan para cada alerta (la primera cuando queda 60 o menos, la segunda cuando queda 30 o menos)
FIRST_ALERT_MINUTES = _int_env("FIRST_ALERT_MINUTES", 60)
SECOND_ALERT_MINUTES = _int_env("SECOND_ALERT_MINUTES", 30)

# Hora (España) del resumen diario y, los lunes, del semanal (0 = medianoche)
SUMMARY_HOUR = _int_env("SUMMARY_HOUR", 0)

# Palabras (separadas por comas) que, si salen en el nombre de un evento, lo marcan como "sin hora exacta" (todo el día).
# Se suman a las de filter.py
ALL_DAY_TITLES = tuple(p.strip().lower() for p in os.environ.get("ALL_DAY_TITLES", "").split(",") if p.strip())
