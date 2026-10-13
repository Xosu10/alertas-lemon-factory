# alertas-lemon-factory

Avisos por Discord de las tormentas de la huerta: cuándo se acercan, cuántas hay hoy y cuántas hay esta semana.

## Qué envía y cuándo

| Mensaje | Cuándo |
|---|---|
| Primera alerta | Cuando falta 1 hora o menos para una tormenta (sale entre 55 y 60 min antes). Lleva `@everyone` |
| Segunda alerta | Cuando faltan 30 minutos o menos (sale entre 25 y 30 min antes). Lleva `@everyone` |
| Resumen diario | De lunes a viernes, a la 01:00 (hora de España). Dice cuántas tormentas hay ese día y a qué hora. Lleva `@everyone` los días con tormenta |
| Resumen semanal | Los lunes, a la 01:00. Lista las tormentas de la semana (lunes a domingo) |

Reglas:

- Cada aviso se envía una sola vez, aunque el servidor se reinicie.
- Las tormentas que salen a la misma hora y minuto se agrupan en un único aviso.
- No se mandan avisos caducados: si la primera alerta ya no llega a tiempo, solo sale la segunda; si la tormenta ya pasó, no se avisa.
- Si cambia la hora de una tormenta, se recalcula y no se avisa a la hora antigua.
- Los eventos sin hora concreta (de todo el día) se ignoran.
- Las horas son de España peninsular (con cambio de hora de verano e invierno) y las fechas salen en español.
- Los lunes, si el calendario aún no trae la semana nueva, los dos resúmenes esperan a que la traiga.

## Cómo funciona

1. **cron-job.org** avisa a GitHub cada 5 minutos (`workflow_dispatch`). El `schedule` propio de GitHub no es fiable a esa frecuencia, por eso solo queda como respaldo.
2. **GitHub Actions** ejecuta `main.py`: descarga el calendario, decide qué toca avisar y lo manda a Discord.
3. El registro de lo ya enviado (`events.db`, SQLite) se guarda en el propio repositorio al terminar cada ejecución.

Todo es gratis: el repositorio es público (minutos de Actions ilimitados) y no se usa ninguna tarjeta.

## Variables

| Variable | Dónde | Por defecto | Qué hace |
|---|---|---|---|
| `DISCORD_WEBHOOK_URL` | Secreto de GitHub (en local, `.env`) | — | Canal de Discord al que se envía |
| `FIRST_ALERT_MINUTES` | Variable de GitHub (opcional) | 60 | Minutos para la primera alerta |
| `SECOND_ALERT_MINUTES` | Variable de GitHub (opcional) | 30 | Minutos para la segunda alerta |
| `SUMMARY_HOUR` | Variable de GitHub (opcional) | 1 | Hora (España) de los resúmenes |

La URL del webhook nunca se escribe en el código ni se sube al repositorio. Se pega desde el portapapeles en
Settings → Secrets and variables → Actions → New repository secret, con el nombre `DISCORD_WEBHOOK_URL`.

## Probar en local

```bash
pip install -r requirements.txt
python preview.py        # imprime todos los mensajes con datos inventados (no envía nada)
python simulate.py       # simula alertas y resúmenes con un reloj virtual (no envía nada)
python probar_discord.py # envía un mensaje de prueba al canal del .env
python ensayo.py         # envía al canal del .env las dos alertas de una tormenta inventada, marcadas como PRUEBA
python reenviar.py ver   # muestra el resumen semanal y el diario de hoy con datos reales (no envía nada)
python reenviar.py       # los envía de nuevo al canal, sin tocar el registro (por si Discord pierde los mensajes)
```

Para `probar_discord.py` hace falta copiar `.env.example` a `.env` y rellenar la URL del webhook.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `main.py` | Arranque: una pasada completa |
| `ciclo.py` | Una pasada: resumen semanal, resumen diario y alertas |
| `tormentas.py` | Agrupa las tormentas simultáneas y decide qué alerta toca |
| `resumenes.py` | Resumen diario y semanal |
| `messages.py` | Todos los textos de los mensajes |
| `filter.py` | Qué eventos cuentan como tormenta |
| `fetch.py` | Descarga del calendario |
| `storage.py`, `envio.py` | Registro de avisos enviados y envío de una sola vez |
| `discord_notifier.py` | Envío a Discord |
| `preview.py`, `simulate.py`, `probar_discord.py`, `ensayo.py`, `reenviar.py` | Herramientas de prueba y de reenvío manual |
| `.github/workflows/avisos.yml` | Ejecución en GitHub Actions |
