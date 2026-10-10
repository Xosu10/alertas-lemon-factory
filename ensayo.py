"""Ensayo real: pasa una tormenta inventada por el mismo código que usa el bot y envía la alerta al canal del .env,
marcada como PRUEBA. Las alertas llevan @everyone, así que cada mensaje avisa a todo el canal.
Por defecto envía solo la primera alerta; con `python ensayo.py completo` envía también la segunda.
Usa un registro temporal, nunca el real."""
import sys
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
    completo = "completo" in sys.argv[1:]

    with tempfile.TemporaryDirectory() as carpeta:
        storage.DB_PATH = str(Path(carpeta) / "ensayo.db")
        storage.init_db()
        ahora = datetime.now(timezone.utc)

        tormentas = [[tormenta_en(ahora, 58)]]
        if completo:
            tormentas.append([tormenta_en(ahora, 28)])

        for eventos in tormentas:
            enviar_alertas(eventos, ahora, enviar_marcado)
        esperados = len(tormentas)
        print(f"Primera pasada: {enviados} mensajes enviados (se esperan {esperados})")

        antes = enviados
        for eventos in tormentas:
            enviar_alertas(eventos, ahora, enviar_marcado)
        print(f"Segunda pasada inmediata: {enviados - antes} mensajes nuevos (se espera 0: nada se repite)")


if __name__ == "__main__":
    main()
