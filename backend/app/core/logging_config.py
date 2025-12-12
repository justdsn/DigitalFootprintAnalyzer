import logging
import sys
import os
from pythonjsonlogger import jsonlogger

def setup_structured_logging():
    """
    Configure root logger for structured JSON logging.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Silence overly verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

# Usage: from app.core.logging_config import setup_structured_logging
# Call setup_structured_logging() at app startup
