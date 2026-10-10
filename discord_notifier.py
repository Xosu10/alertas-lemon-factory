import requests

from config import DISCORD_WEBHOOK_URL


def send_discord_message(content):
    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError("Falta configurar DISCORD_WEBHOOK_URL en el archivo .env")

    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content}, timeout=10)
    response.raise_for_status()
