from dataclasses import dataclass
from datetime import datetime

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

AVISO_NOCTURNO_RESUMEN = (
    "🌙 Ojo, que de madrugada el tiempo anda revuelto: no te vayas al huerto de noche, "
    "que con la tormenta y a oscuras no se ve ni el capazo. "
    "¡Mejor esperar a que aclare o estate bien atento!"
)
AVISO_NOCTURNO_ALERTA = "🌙 Y es de madrugada: nada de ir al huerto a oscuras, que el tiempo anda revuelto."


@dataclass
class Tormenta:
    cuando: datetime  # siempre en hora de España
    cantidad: int = 1  # cuántas salen a esa misma hora y minuto


def fecha_larga(dt):
    return f"{DIAS[dt.weekday()]} {dt.day} de {MESES[dt.month - 1]}"


def hora(dt):
    return dt.strftime("%H:%M")


def es_de_madrugada(tormenta):
    """De 00:00 a 06:00, ambas incluidas (hora de España)."""
    t = tormenta.cuando
    return t.hour < 6 or (t.hour == 6 and t.minute == 0)


def _minutos(n):
    return f"{n} minuto" if n == 1 else f"{n} minutos"


def _aviso_juntas(cantidad):
    if cantidad < 2:
        return ""
    return f"\n\n⚠️ Ojo: no viene una sola, vienen {cantidad} tormentas juntas a la misma hora."


def _aviso_nocturno(de_madrugada):
    return f"\n\n{AVISO_NOCTURNO_ALERTA}" if de_madrugada else ""


def _item(tormenta, con_fecha):
    juntas = f" (vienen {tormenta.cantidad} juntas)" if tormenta.cantidad > 1 else ""
    if con_fecha:
        fecha = fecha_larga(tormenta.cuando)
        return f"• {fecha[0].upper() + fecha[1:]} — {hora(tormenta.cuando)} ⛈️{juntas}"
    madrugada = " 🌙 de madrugada" if es_de_madrugada(tormenta) else ""
    return f"• {hora(tormenta.cuando)} ⛈️{madrugada}{juntas}"


def primera_alerta(minutos, tormenta):
    return (
        "@everyone ⛈️ ¡Atención, zagales! Se viene una buena tormenta\n\n"
        f"🕒 {fecha_larga(tormenta.cuando)} {hora(tormenta.cuando)} (hora España)\n\n"
        f"En {_minutos(minutos)} se puede liar parda por la huerta. "
        "¡Recoge los limones, guarda las herramientas y ponte a cubierto, que vienen curvas!"
        + _aviso_juntas(tormenta.cantidad)
        + _aviso_nocturno(es_de_madrugada(tormenta))
    )


def segunda_alerta(minutos, cantidad=1, de_madrugada=False):
    return (
        "@everyone 🚨 ¡Alerta roja en el bancal!\n\n"
        "El cielo se está poniendo más negro que un capazo de tierra mojada. "
        f"En {_minutos(minutos)} llega una tormenta bien gorda. "
        "¡Que no te pille con el tractor arrancado y los limones sin recoger!"
        + _aviso_juntas(cantidad)
        + _aviso_nocturno(de_madrugada)
    )


def resumen_diario(dia, tormentas):
    fecha = fecha_larga(dia)

    if not tormentas:
        return (
            "🌤️ Parte meteorológico de la huerta\n\n"
            f"📅 Resumen del día ({fecha}): no parece que vaya a haber tormenta, "
            "ha escampado y hace mu buen temporal, te puedes beber una estrella levante "
            "a la sombra del limonero\n\n"
            "Puedes echar el día tranquilo, regar los limoneros y recoger la cosecha "
            "sin miedo a que te pille una tormenta de las gordas."
        )

    n = len(tormentas)
    cuantas = "se espera 1 tormenta de las gordas" if n == 1 else f"se esperan {n} tormentas de las gordas"
    lista = "\n".join(_item(t, con_fecha=False) for t in tormentas)
    nocturno = f"{AVISO_NOCTURNO_RESUMEN}\n\n" if any(es_de_madrugada(t) for t in tormentas) else ""
    return (
        "@everyone 🌥️ Parte meteorológico de la huerta\n\n"
        f"📅 Resumen del día ({fecha}): hoy el cielo viene cargado, {cuantas}:\n\n"
        f"{lista}\n\n"
        f"{nocturno}"
        "No te confíes: ten los limones recogidos y las herramientas a mano. "
        "¡Te iremos avisando antes de cada una!"
    )


def resumen_semanal(tormentas):
    if not tormentas:
        return (
            "🍋 Semana de cosecha tranquila\n\n"
            "☀️ Parte semanal de la huerta: no se prevén tormentas, puedes salirte al huerto "
            "a tomarte una estrella levante a la sombra del limonero.\n\n"
            "El huertano puede trabajar a su ritmo, revisar el riego y echarle un ojo a los limoneros. "
            "¡Semana de poca nube y mucho bancal!"
        )

    n = len(tormentas)
    cuantas = "se espera 1 tormenta bien gorda" if n == 1 else f"se esperan {n} tormentas bien gordas"
    lista = "\n".join(_item(t, con_fecha=True) for t in tormentas)
    return (
        "🌪️ Semana de mucho meneo en la huerta\n\n"
        f"🗓️ Resumen semanal: {cuantas} esta semana.\n\n"
        f"{lista}\n\n"
        "Deja los bancales preparados, recoge lo que puedas y no te confíes: "
        "esta semana el tiempo viene revuelto."
    )
