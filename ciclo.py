from filter import filtrar_tormentas, filtrar_tormentas_sin_hora
from resumenes import enviar_resumen_diario, enviar_resumen_semanal
from tormentas import enviar_alertas


def comprobar(todos, ahora, enviar):
    """Una pasada completa: resumen semanal, resumen diario y alertas. `todos` es el calendario sin filtrar.
    Las tormentas sin hora exacta (de todo el día) solo salen en los resúmenes: no hay hora para avisar antes."""
    con_hora = filtrar_tormentas(todos)
    sin_hora = filtrar_tormentas_sin_hora(todos)
    enviar_resumen_semanal(todos, con_hora, sin_hora, ahora, enviar)
    enviar_resumen_diario(todos, con_hora, sin_hora, ahora, enviar)
    enviar_alertas(con_hora, ahora, enviar)
