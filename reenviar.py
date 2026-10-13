"""Reenvía a mano el resumen semanal y el diario de hoy con los datos reales, sin tocar el registro de avisos.
Sirve si Discord pierde los mensajes. `python reenviar.py ver` solo los muestra, sin enviar nada."""
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

from discord_notifier import send_discord_message
from fetch import get_events
from filter import filtrar_tormentas
from messages import resumen_diario, resumen_semanal
from tormentas import agrupar

MADRID = ZoneInfo("Europe/Madrid")


def _fecha_madrid(evento):
    return datetime.fromisoformat(evento["date"]).astimezone(MADRID).date()


def _descargar_calendario():
    """Si el calendario pide esperar (error 429), reintenta cada 30 segundos hasta 5 veces."""
    for intento in range(6):
        try:
            return get_events()
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code != 429 or intento == 5:
                raise
            print("El calendario pide esperar un poco; reintento en 30 segundos...", flush=True)
            time.sleep(30)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    solo_ver = "ver" in sys.argv[1:]

    ahora = datetime.now(timezone.utc).astimezone(MADRID)
    hoy = ahora.date()
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    tormentas = filtrar_tormentas(_descargar_calendario())

    semanal = resumen_semanal(agrupar([e for e in tormentas if lunes <= _fecha_madrid(e) <= domingo]))
    diario = resumen_diario(ahora, agrupar([e for e in tormentas if _fecha_madrid(e) == hoy]))

    for nombre, texto in (("RESUMEN SEMANAL", semanal), ("RESUMEN DIARIO", diario)):
        print("=" * 60)
        print(nombre)
        print("=" * 60)
        print(texto)
        print()
        if not solo_ver:
            send_discord_message(texto)

    print("Solo vista previa, no se ha enviado nada." if solo_ver else "Enviados los dos mensajes.")


if __name__ == "__main__":
    main()
