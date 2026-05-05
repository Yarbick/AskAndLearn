"""Запуск"""

# Главное приложение
from app import app

# Работа с виртуальным окружением
from os import getenv


def main():
    # Запуск приложения
    port: int = getenv("PORT", 5000)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
