import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import get_settings

_DEFAULT_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())


class JsonFormatter(logging.Formatter):
    """Formatea cada línea de log como un objeto JSON de una sola línea.

    Facilita ingerir los logs en cualquier plataforma de observabilidad
    (Datadog, CloudWatch, Loki, ...) sin parsers ad-hoc.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extras = {k: v for k, v in record.__dict__.items() if k not in _DEFAULT_RECORD_ATTRS}
        payload.update(extras)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level)
