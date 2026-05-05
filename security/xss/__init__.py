"""Функции и методы для защиты от XSS-атак"""

# Безопасность
import bleach


def clean_html(data: str | dict) -> str | dict:
    """Очистка данных от HTML"""

    if isinstance(data, str):  # Очистка строки (для данных с форм)
        cleared_data: str = bleach.clean(
            data,
            tags=set(),
            attributes={},
            strip=True,
            strip_comments=True
        ).strip()
    elif isinstance(data, dict):  # Очистка словаря с данным (для данных из парсеров)
        # Чистим значения, которые являются строками
        cleared_data: dict = {
            (clean_html(key) if isinstance(key, str) else key): (clean_html(value) if isinstance(value, str) else value)
            for key, value in data.items()
        }
    else:
        raise TypeError("Invalid data type")

    return cleared_data
