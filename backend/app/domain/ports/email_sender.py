from typing import Protocol


class EmailSender(Protocol):
    """Puerto para enviar emails.

    A diferencia de `domain/repositories`, esto no es persistencia sino un
    servicio externo — se agrupa en `domain/ports` para reflejar esa
    diferencia. Ver ADR 0009.
    """

    async def send(self, to: str, subject: str, body: str) -> None: ...
