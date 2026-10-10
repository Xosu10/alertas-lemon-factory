"""Vista previa: imprime los mensajes con datos inventados. No envía nada a Discord."""
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from messages import (
    Tormenta,
    primera_alerta,
    resumen_diario,
    resumen_semanal,
    segunda_alerta,
)

MADRID = ZoneInfo("Europe/Madrid")


def madrid(dia, hora, minuto):
    return datetime(2026, 10, dia, hora, minuto, tzinfo=MADRID)


def mostrar(titulo, texto):
    print("=" * 64)
    print(titulo)
    print("=" * 64)
    print(texto)
    print(f"\n({len(texto)} caracteres)\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    sola = Tormenta(madrid(14, 20, 30))
    junta = Tormenta(madrid(14, 20, 0), cantidad=3)

    miercoles = [Tormenta(madrid(14, 14, 30)), junta]
    semana = [Tormenta(madrid(12, 14, 30))] + miercoles + [Tormenta(madrid(16, 14, 30))]

    mostrar("1) PRIMERA ALERTA (unos 55 min antes)", primera_alerta(55, sola))
    mostrar("2) SEGUNDA ALERTA (unos 29 min antes)", segunda_alerta(29))
    mostrar("3) RESUMEN DIARIO - sin tormentas", resumen_diario(madrid(14, 1, 0), []))
    mostrar("4) RESUMEN DIARIO - con tormentas (PROPUESTA)", resumen_diario(madrid(14, 1, 0), miercoles))
    mostrar("5) RESUMEN SEMANAL - con tormentas", resumen_semanal(semana))
    mostrar("6) RESUMEN SEMANAL - sin tormentas", resumen_semanal([]))

    print("#" * 64)
    print("VARIANTES")
    print("#" * 64 + "\n")
    mostrar("1b) Primera alerta con 3 tormentas a la misma hora (PROPUESTA)", primera_alerta(55, junta))
    mostrar("2b) Segunda alerta con 3 tormentas a la misma hora (PROPUESTA)", segunda_alerta(29, cantidad=3))
    mostrar("5b) Resumen semanal con 1 sola tormenta", resumen_semanal([Tormenta(madrid(15, 14, 30))]))


if __name__ == "__main__":
    main()
