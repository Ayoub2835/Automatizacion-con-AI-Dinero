import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import Settings


class SmtpEmailSender:
    """Implementación concreta de EmailSender sobre SMTP estándar.

    `smtplib` es bloqueante; se ejecuta en un hilo aparte (`asyncio.to_thread`)
    para no bloquear el event loop de FastAPI.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, to: str, subject: str, body: str) -> None:
        await asyncio.to_thread(self._send_sync, to, subject, body)

    def _send_sync(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._settings.smtp_from_email
        message["To"] = to
        message.set_content(body)

        with smtplib.SMTP(self._settings.smtp_host, self._settings.smtp_port, timeout=10) as smtp:
            if self._settings.smtp_use_tls:
                smtp.starttls()
            if self._settings.smtp_username and self._settings.smtp_password:
                smtp.login(self._settings.smtp_username, self._settings.smtp_password)
            smtp.send_message(message)
