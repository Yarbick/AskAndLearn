"""Запуск"""

# WSGI сервер
from waitress import serve

# Настройки сервера
from config import Config

# Главное приложение
from app import app


def main() -> None:
    """Запуск приложения"""

    # Логи
    print("\nLaunched the Waitress server...")
    print("Press CTRL+C to stop the server")

    # Запуск сервера
    serve(
        app,
        host=Config.HOST,
        port=Config.PORT,
        threads=Config.THREADS,
        max_request_header_size=Config.MAX_REQUEST_HEADER_SIZE,
        max_request_body_size=Config.MAX_REQUEST_BODY_SIZE,
        channel_timeout=Config.CHANNEL_TIMEOUT,
        cleanup_interval=Config.CLEANUP_INTERVAL
    )


if __name__ == "__main__":
    main()
