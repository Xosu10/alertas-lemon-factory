"""Ensayo real: pasa tormentas inventadas por el mismo código que usa el bot y envía las alertas al canal del .env.
Cada mensaje lleva delante una línea de PRUEBA. Usa un registro temporal, nunca el real."""
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import storage
from discord_notifier import send_discord_message
from tormentas import enviar_alertas

NUEVA_YORK = ZoneInfo("America/New_York")
MARCA = "🧪 Ensayo, ignóralo: esto es una prueba del aviso.\n\n"
enviados = 0


def enviar_marcado(texto):
    global enviados
    send_discord_message(MARCA + texto)
    enviados += 1


def tormenta_en(ahora, minutos):
    cuando = (ahora + timedelta(minutes=minutos)).replace(second=0, microsecond=0)
    return {
        "title": "Evento de ensayo",
        "country": "USD",
        "date": cuando.astimezone(NUEVA_YORK).isoformat(),
        "impact": "High",
        "forecast": "",
        "previous": "",
    }


def main():
    with tempfile.TemporaryDirectory() as carpeta:
        storage.DB_PATH = str(Path(carpeta) / "ensayo.db")
        storage.init_db()
        ahora = datetime.now(timezone.utc)

        primera = [tormenta_en(ahora, 58)]
        segunda = [tormenta_en(ahora, 28)]

        enviar_alertas(primera, ahora, enviar_marcado)
        enviar_alertas(segunda, ahora, enviar_marcado)
        print(f"Primera pasada: {enviados} mensajes enviados (se esperan 2: primera y segunda alerta)")

        antes = enviados
        enviar_alertas(primera, ahora, enviar_marcado)
        enviar_alertas(segunda, ahora, enviar_marcado)
        print(f"Segunda pasada inmediata: {enviados - antes} mensajes nuevos (se espera 0: nada se repite)")


if __name__ == "__main__":
    main()
