"""Envía un mensaje de prueba al canal configurado en DISCORD_WEBHOOK_URL (archivo .env)."""
from discord_notifier import send_discord_message

send_discord_message("🍋 Prueba de conexión del aviso de la huerta. Si ves este mensaje, todo está en marcha.")
print("Mensaje de prueba enviado. Revisa el canal de Discord.")
