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
