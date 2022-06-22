from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel


class User(BaseModel):
    """Basic user model"""
    user_name: str
    role_name: str
    role_description: Union[str, None] = None
    password_hash: Union[Any, None] = None  # Remove later


class Downtime(BaseModel):
    """Downtime model"""
    start_time: datetime
    end_time: datetime
    comment: str
    user_name: str


class JWT(BaseModel):
    """JWT model"""
    token_type: str = "bearer"
    access_token: str = "your-access-token"
    refresh_token: str = "your-one-time-refresh-token"


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "SwtichController"
    LOG_FORMAT: str = "%(asctime)s | %(levelprefix)s | %(message)s"
    LOG_LEVEL: str = "TRACE"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "SwtichController": {"handlers": ["default"], "level": LOG_LEVEL},
    }