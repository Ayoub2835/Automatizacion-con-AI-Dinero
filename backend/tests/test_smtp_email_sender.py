import socket
from email import message_from_bytes

from aiosmtpd.controller import Controller

from app.core.config import Settings
from app.infrastructure.external.smtp_email_sender import SmtpEmailSender


class _RecordingHandler:
    def __init__(self) -> None:
        self.envelopes: list = []

    async def handle_DATA(self, server, session, envelope):  # noqa: N802, ANN001
        self.envelopes.append(envelope)
        return "250 OK"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


async def test_smtp_email_sender_sends_a_real_message_over_smtp() -> None:
    """Prueba SmtpEmailSender contra un servidor SMTP real (no un mock),
    para verificar que el protocolo/formato del mensaje es correcto de
    verdad, no solo que se llamó a una función."""
    handler = _RecordingHandler()
    port = _free_port()
    controller = Controller(handler, hostname="127.0.0.1", port=port)
    controller.start()
    try:
        settings = Settings(
            secret_key="test-secret",
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            smtp_host="127.0.0.1",
            smtp_port=port,
            smtp_from_email="no-reply@gestoria.local",
        )
        sender = SmtpEmailSender(settings)

        await sender.send(
            to="cliente@example.com",
            subject="Asunto de prueba",
            body="Cuerpo de prueba",
        )

        assert len(handler.envelopes) == 1
        envelope = handler.envelopes[0]
        assert envelope.rcpt_tos == ["cliente@example.com"]
        assert envelope.mail_from == "no-reply@gestoria.local"

        message = message_from_bytes(envelope.content)
        assert message["Subject"] == "Asunto de prueba"
        assert message["To"] == "cliente@example.com"
    finally:
        controller.stop()
