import requests

from config import DISCORD_WEBHOOK_URL


def send_discord_message(content):
    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError("Falta configurar DISCORD_WEBHOOK_URL en el archivo .env")

    # Solo se permite la mención a todo el canal (@everyone); cualquier otra mención queda sin efecto.
    payload = {"content": content, "allowed_mentions": {"parse": ["everyone"]}}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
