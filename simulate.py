"""Simulación de las alertas con reloj virtual y eventos falsos.
No envía nada a Discord y usa un registro temporal, nunca el real."""
import re
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import storage
from ciclo import comprobar
from filter import filtrar_tormentas
from tormentas import enviar_alertas

MADRID = ZoneInfo("Europe/Madrid")
NUEVA_YORK = ZoneInfo("America/New_York")
PASO = timedelta(minutes=5)


def madrid(mes, dia, hora, minuto, segundo=0):
    return datetime(2026, mes, dia, hora, minuto, segundo, tzinfo=MADRID)


def evento(cuando, impacto="High", pais="USD"):
    return {
        "title": "Evento de prueba",
        "country": pais,
        "date": cuando.astimezone(NUEVA_YORK).isoformat(),
        "impact": impacto,
        "forecast": "",
        "previous": "",
    }


def describir(texto):
    if texto.startswith(("⛈️", "🚨")):
        tipo = "primera" if texto.startswith("⛈️") else "segunda"
        minutos = re.search(r"En (\d+) minuto", texto).group(1)
        juntas = re.search(r"vienen (\d+) tormentas juntas", texto)
        extra = f", {juntas.group(1)} tormentas juntas" if juntas else ""
        return tipo, f"{tipo.upper()} alerta (dice «en {minutos} min»{extra})"

    tipo = "diario" if texto.startswith(("🌥️", "🌤️")) else "semanal"
    con_tormentas = texto.startswith(("🌥️", "🌪️"))
    return tipo, f"RESUMEN {tipo.upper()} ({'con' if con_tormentas else 'sin'} tormentas)"


def simular(nombre, feed, inicio, fin, esperado, mostrar_textos=False, comprobar_extra=None, resumenes=False, con_dia=False):
    """`feed(ahora)` devuelve los eventos que publica el calendario en ese momento."""
    print("=" * 72)
    print(nombre)
    print("=" * 72)

    enviados = []
    with tempfile.TemporaryDirectory() as carpeta:
        storage.DB_PATH = str(Path(carpeta) / "simulacion.db")
        storage.init_db()

        ahora = inicio
        while ahora <= fin:
            todos = feed(ahora)
            for _ in range(2):  # la segunda pasada simula un reinicio o una ejecución repetida: no debe duplicar nada
                entregar = lambda texto, a=ahora: enviados.append((a, texto))
                if resumenes:
                    comprobar(todos, ahora, entregar)
                else:
                    enviar_alertas(filtrar_tormentas(todos), ahora, entregar)
            ahora += PASO

    formato = "%d/%m %H:%M" if con_dia else "%H:%M"
    obtenido = []
    vistos = set()
    for momento, texto in enviados:
        tipo, descripcion = describir(texto)
        obtenido.append((momento.strftime(formato), tipo))
        print(f"  {momento.strftime('%d/%m %H:%M:%S' if con_dia else '%H:%M:%S')}  ->  {descripcion}")
        if mostrar_textos and tipo not in vistos:
            vistos.add(tipo)
            print()
            print("\n".join("        | " + linea for linea in texto.split("\n")))
            print()
    if not enviados:
        print("  (no se envía nada)")

    correcto = obtenido == esperado and (comprobar_extra is None or comprobar_extra(enviados))
    print(f"\n  Esperado: {esperado if esperado else 'nada'}")
    print("  OK, CORRECTO" if correcto else "  FALLO, NO COINCIDE")
    print()
    return correcto


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("El reloj virtual avanza de 5 en 5 minutos, como el disparador real.")
    print("Cada comprobación se ejecuta dos veces seguidas para verificar que nada se duplica.\n")

    una = [evento(madrid(10, 14, 20, 30))]

    def cambia_la_hora(ahora):
        if ahora < madrid(10, 14, 19, 10):
            return [evento(madrid(10, 14, 20, 0))]
        return [evento(madrid(10, 14, 21, 0))]

    def no_cuentan(ahora):
        return [
            evento(madrid(10, 14, 20, 30), impacto="Medium"),
            evento(madrid(10, 14, 20, 30), pais="EUR"),
            {
                "title": "Evento de todo el día",
                "country": "USD",
                "date": "2026-10-14T00:00:00-04:00",
                "impact": "High",
                "forecast": "",
                "previous": "",
            },
        ]

    cambio_horario = [
        {
            "title": "Evento tras el cambio de hora",
            "country": "USD",
            "date": "2026-10-28T14:30:00-04:00",
            "impact": "High",
            "forecast": "",
            "previous": "",
        }
    ]

    def ruido(dias):
        """Eventos que no son tormentas (impacto medio u otro país) para que el calendario no esté vacío."""
        return [
            e
            for dia in dias
            for e in (
                evento(madrid(10, dia, 3, 0), impacto="Low", pais="EUR"),
                evento(madrid(10, dia, 14, 30), impacto="Medium"),
            )
        ]

    # Semana del domingo 11 al sábado 17 de octubre, con 4 tormentas (una de ellas con 3 eventos a la vez)
    semana = ruido(range(12, 17)) + [
        evento(madrid(10, 12, 14, 30)),
        evento(madrid(10, 14, 14, 30)),
        *[evento(madrid(10, 14, 20, 0))] * 3,
        evento(madrid(10, 16, 14, 30)),
    ]
    semana_vieja = ruido(range(5, 10)) + [evento(madrid(10, 7, 20, 0))]
    tranquila = ruido(range(12, 17))
    tranquila_19 = ruido(range(19, 24))

    resultados = [
        simular(
            "A) Una tormenta a las 20:30 (miércoles 14 de octubre)",
            lambda ahora: una,
            madrid(10, 14, 19, 2, 40),
            madrid(10, 14, 20, 40, 40),
            [("19:32", "primera"), ("20:02", "segunda")],
            mostrar_textos=True,
        ),
        simular(
            "B) Datos reales del 16 de septiembre: 3 tormentas a las 20:00 y otra a las 20:30",
            lambda ahora: [evento(madrid(9, 16, 20, 0))] * 3 + [evento(madrid(9, 16, 20, 30))],
            madrid(9, 16, 19, 2, 40),
            madrid(9, 16, 20, 40, 40),
            [("19:02", "primera"), ("19:32", "segunda"), ("19:32", "primera"), ("20:02", "segunda")],
            mostrar_textos=True,
        ),
        simular(
            "C1) El bot arranca tarde, con 45 minutos para la tormenta de las 20:30",
            lambda ahora: una,
            madrid(10, 14, 19, 45, 10),
            madrid(10, 14, 20, 40, 10),
            [("19:45", "primera"), ("20:00", "segunda")],
        ),
        simular(
            "C2) El bot arranca con solo 25 minutos: ya no hay primera alerta, solo la segunda",
            lambda ahora: una,
            madrid(10, 14, 20, 5, 10),
            madrid(10, 14, 20, 40, 10),
            [("20:05", "segunda")],
        ),
        simular(
            "C3) El bot arranca cuando la tormenta ya pasó: no avisa",
            lambda ahora: una,
            madrid(10, 14, 20, 40, 10),
            madrid(10, 14, 20, 55, 10),
            [],
        ),
        simular(
            "D) Cambia la hora: la tormenta de las 20:00 pasa a las 21:00 a las 19:10",
            cambia_la_hora,
            madrid(10, 14, 19, 2, 40),
            madrid(10, 14, 21, 10, 40),
            [("19:02", "primera"), ("20:02", "primera"), ("20:32", "segunda")],
        ),
        simular(
            "E) Cosas que no cuentan: impacto medio, otro país y un evento de todo el día",
            no_cuentan,
            madrid(10, 14, 5, 2, 40),
            madrid(10, 14, 20, 40, 40),
            [],
        ),
        simular(
            "F) Cambio de hora de España: 14:30 de Nueva York es 19:30 en España el 28 de octubre",
            lambda ahora: cambio_horario,
            madrid(10, 28, 18, 2, 40),
            madrid(10, 28, 19, 40, 40),
            [("18:32", "primera"), ("19:02", "segunda")],
            comprobar_extra=lambda enviados: "miércoles 28 de octubre 19:30 (hora España)" in enviados[0][1],
        ),
        simular(
            "G1) Resumen diario con tormentas: miércoles 14 de octubre, a la 01:00",
            lambda ahora: semana,
            madrid(10, 14, 0, 32, 40),
            madrid(10, 14, 1, 30, 40),
            [("01:02", "diario")],
            mostrar_textos=True,
            resumenes=True,
        ),
        simular(
            "G2) Resumen diario sin tormentas: martes 13 de octubre",
            lambda ahora: semana,
            madrid(10, 13, 0, 32, 40),
            madrid(10, 13, 1, 30, 40),
            [("01:02", "diario")],
            mostrar_textos=True,
            resumenes=True,
        ),
        simular(
            "G3) El resumen diario sale una vez al día, dos días seguidos",
            lambda ahora: tranquila,
            madrid(10, 14, 0, 32, 40),
            madrid(10, 15, 1, 30, 40),
            [("14/10 01:02", "diario"), ("15/10 01:02", "diario")],
            resumenes=True,
            con_dia=True,
        ),
        simular(
            "G4) Lunes 12 de octubre completo: resumen semanal, resumen diario y las dos alertas de las 14:30",
            lambda ahora: semana,
            madrid(10, 12, 0, 32, 40),
            madrid(10, 12, 23, 55, 40),
            [("01:02", "semanal"), ("01:02", "diario"), ("13:32", "primera"), ("14:02", "segunda")],
            mostrar_textos=True,
            resumenes=True,
        ),
        simular(
            "G5) El calendario sigue con la semana vieja hasta las 09:00: los resúmenes del lunes esperan",
            lambda ahora: semana_vieja if ahora < madrid(10, 12, 9, 0) else semana,
            madrid(10, 12, 0, 32, 40),
            madrid(10, 12, 10, 0, 40),
            [("09:02", "semanal"), ("09:02", "diario")],
            resumenes=True,
        ),
        simular(
            "G6) Semana sin tormentas: lunes 19 de octubre",
            lambda ahora: tranquila_19,
            madrid(10, 19, 0, 32, 40),
            madrid(10, 19, 1, 30, 40),
            [("01:02", "semanal"), ("01:02", "diario")],
            mostrar_textos=True,
            resumenes=True,
        ),
        simular(
            "H) Una tormenta que en Nueva York es domingo por la tarde, pero en España ya es lunes (01:30)",
            lambda ahora: semana + [evento(madrid(10, 12, 1, 30))],
            madrid(10, 12, 0, 2, 40),
            madrid(10, 12, 1, 40, 40),
            [("00:32", "primera"), ("01:02", "semanal"), ("01:02", "diario"), ("01:02", "segunda")],
            mostrar_textos=True,
            resumenes=True,
        ),
        simular(
            "I) Fin de semana: el diario sale el viernes, ni sábado ni domingo, y el lunes salen semanal y diario",
            lambda ahora: tranquila + tranquila_19,
            madrid(10, 16, 0, 32, 40),
            madrid(10, 19, 1, 30, 40),
            [("16/10 01:02", "diario"), ("19/10 01:02", "semanal"), ("19/10 01:02", "diario")],
            resumenes=True,
            con_dia=True,
        ),
    ]

    correctos = sum(resultados)
    print(f"RESULTADO: {correctos} de {len(resultados)} escenarios correctos")
    sys.exit(0 if correctos == len(resultados) else 1)


if __name__ == "__main__":
    main()
