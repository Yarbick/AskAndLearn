"""Настройки сервера"""

# Работа с виртуальным окружением
from os import getenv

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class Config:
    """Настройки сервера"""

    # Параметры
    HOST: str = "127.0.0.1"
    PORT: int = getenv("PORT", 5000)
    THREADS: int = 4
    MAX_REQUEST_HEADER_SIZE: int = 1024 * 16
    MAX_REQUEST_BODY_SIZE: int = 1024 * 1024 * 100
    CHANNEL_TIMEOUT: int = 120
    CLEANUP_INTERVAL: int = 30
