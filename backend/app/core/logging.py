from __future__ import annotations

import logging
from logging.config import dictConfig
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = "/app/backend/logs/backend.log") -> None:
    log_path = Path(log_file)
    handlers: dict[str, dict] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "default",
        },
    }
    handler_names = ["console"]

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "default",
            "filename": str(log_path),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        }
        handler_names.append("file")
    except OSError:
        # Fallback to console-only if file system is read-only or path is invalid
        pass

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": handlers,
            "root": {
                "level": level,
                "handlers": handler_names,
            },
            "loggers": {
                "uvicorn": {
                    "level": level,
                    "handlers": handler_names,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": level,
                    "handlers": handler_names,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": handler_names,
                    "propagate": False,
                },
                # watchfiles in uvicorn reload mode forces its own root logger
                # to INFO and emits "1 change detected" for every file mutation,
                # which floods the log. Pin to WARNING.
                "watchfiles": {
                    "level": "WARNING",
                    "handlers": handler_names,
                    "propagate": False,
                },
                "watchfiles.main": {
                    "level": "WARNING",
                    "handlers": handler_names,
                    "propagate": False,
                },
            },
        }
    )
