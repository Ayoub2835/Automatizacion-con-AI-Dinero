class DomainError(Exception):
    """Excepción base para todos los errores de dominio.

    `app/core/exceptions.py` traduce estas excepciones a respuestas HTTP.
    El dominio no conoce HTTP ni FastAPI.
    """


class EntityNotFoundError(DomainError):
    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} con id '{identifier}' no encontrado")


class AlreadyExistsError(DomainError):
    def __init__(self, entity: str, field: str, value: str) -> None:
        self.entity = entity
        self.field = field
        self.value = value
        super().__init__(f"Ya existe {entity} con {field} '{value}'")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Credenciales inválidas")


class InvalidStateTransitionError(DomainError):
    """Una operación que solo es válida en ciertos estados (ej. aprobar una
    Publication) se intenta desde un estado que no lo permite — ver ADR 0014."""

    def __init__(self, entity: str, from_state: str, action: str) -> None:
        self.entity = entity
        self.from_state = from_state
        self.action = action
        super().__init__(f"No se puede '{action}' {entity} en estado '{from_state}'")
