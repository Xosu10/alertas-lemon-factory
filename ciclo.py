from filter import filtrar_tormentas
from resumenes import enviar_resumen_diario, enviar_resumen_semanal
from tormentas import enviar_alertas


def comprobar(todos, ahora, enviar):
    """Una pasada completa: resumen semanal, resumen diario y alertas. `todos` es el calendario sin filtrar."""
    filtrados = filtrar_tormentas(todos)
    enviar_resumen_semanal(todos, filtrados, ahora, enviar)
    enviar_resumen_diario(todos, filtrados, ahora, enviar)
    enviar_alertas(filtrados, ahora, enviar)
