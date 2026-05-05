"""Запуск"""

# Главное приложение
from app import app

# Работа с виртуальным окружением
from os import environ


def main():
    # Запуск приложения
    port: int = environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
