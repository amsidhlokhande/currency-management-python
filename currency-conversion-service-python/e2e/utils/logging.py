"""
JSON Logging Utility with Automatic PII Masking Filter.
"""
import logging
import re
import json
from datetime import datetime, timezone
from flask import g, has_request_context
import constants

class PIIMaskingFilter(logging.Filter):
    """
    Scrubs PII (Personally Identifiable Information) such as emails,
    credit cards, account numbers, and bearer tokens from logs.
    """
    EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    CARD_REGEX = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b')
    ACCOUNT_REGEX = re.compile(r'\b\d{9,18}\b')
    BEARER_REGEX = re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE)

    def mask_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        text = self.EMAIL_REGEX.sub(r'\1[at]***.com', text)
        text = self.CARD_REGEX.sub(r'****-****-****-XXXX', text)
        text = self.ACCOUNT_REGEX.sub(r'***ACCOUNT***', text)
        text = self.BEARER_REGEX.sub(r'\1[REDACTED_TOKEN]', text)
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_text(record.msg)
        if isinstance(record.args, dict):
            record.args = {k: self.mask_text(v) if isinstance(v, str) else v for k, v in record.args.items()}
        elif isinstance(record.args, (list, tuple)):
            record.args = tuple(self.mask_text(v) if isinstance(v, str) else v for v in record.args)
        return True


class JsonLogFormatter(logging.Formatter):
    """
    Structured JSON log formatter outputting machine-readable JSON logs
    with ISO timestamps, trace/correlation IDs, and service metadata.
    """
    def format(self, record: logging.LogRecord) -> str:
        correlation_id = getattr(record, "correlation_id", None)
        if not correlation_id and has_request_context():
            correlation_id = getattr(g, "correlation_id", "NO_CORRELATION_ID")

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": constants.SERVICE_NAME,
            "correlationId": correlation_id or "SYSTEM",
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "lineno": record.lineno,
        }

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging(level_name: str = "INFO") -> logging.Logger:
    """Configures root logger with JSON formatting and PII filter."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    handler.addFilter(PIIMaskingFilter())
    logger.addHandler(handler)
    return logger
