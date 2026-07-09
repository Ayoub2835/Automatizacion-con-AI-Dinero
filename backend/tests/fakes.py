from dataclasses import dataclass


@dataclass
class SentEmail:
    to: str
    subject: str
    body: str


class FakeEmailSender:
    """Doble de prueba de EmailSender: registra los emails en memoria en vez
    de enviarlos, para que los tests de integración no dependan de un SMTP
    real. SmtpEmailSender en sí se prueba aparte contra un servidor SMTP
    real (ver test_smtp_email_sender.py)."""

    def __init__(self) -> None:
        self.sent: list[SentEmail] = []

    async def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append(SentEmail(to=to, subject=subject, body=body))
