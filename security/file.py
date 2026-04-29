"""Защита от атак через файлы"""

# Работа с файлами
import re
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_wtf.file import FileAllowed

# Работа с изображениями
import imghdr

# Типизация
from io import BytesIO


class File:
    """Общая проверка для всех типов файлов"""

    @staticmethod
    def create_secure_name(filename: str) -> str:
        """Создание безопасного имени файла, для избежания атаки через название"""

        return secure_filename(filename)

    @staticmethod
    def check_extension(filename: str, correct_extensions: list | tuple = ("jpg", "jpeg", "png", "webp")) -> bool:
        """Базовая проверка на правильное расширение файла, чтобы избежать загрузки вредоносного кода"""

        # Определение расширения файла
        file_extension: str = filename.split(".")[-1]
        # Проверка
        return file_extension in correct_extensions

    @staticmethod
    def full_clearing_filename(filename: str) -> str:
        """Полная очистка имени файла"""

        # Очистка имени от недопустимых символов
        cleared_filename: str = File.clear_filename(filename)
        # Обрезание имени файла до допустимых размеров
        cutted_filename: str = File.cut_filename(filename)

        return cleared_filename

    @staticmethod
    def clear_filename(filename: str) -> str:
        """Очистка имени файла от недопустимых в файловой системе символов, чтобы избежать ошибки на сервере"""

        # Замена недопустимых символов подчёркиванием
        cleared_filename: str = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Удаление лишних подчёркиваний и пробелов
        cleared_filename: str = re.sub(r'_+', '_', cleared_filename).strip('_')

        return cleared_filename

    @staticmethod
    def cut_filename(filename: str) -> str:
        """Обрезание имени файла до допустимых размеров (с запасом), чтобы избежать ошибки на сервере"""

        return filename[:255]


class Image(File):
    """Проверка изображений"""

    @staticmethod
    def full_check(filename: str, correct_extensions: list | tuple, stream: BytesIO) -> tuple[bool, str, str]:
        """Полная проверка изображения"""

        # Создание безопасного имени файла
        secured_filename: str = Image.create_secure_name(filename)

        # Проверки
        if Image.check_extension(secured_filename, correct_extensions):  # Проверка расширения
            if Image.check_mime_type(stream):  # Проверка MIME-типа
                return True, "OK", secured_filename
            return False, "The file is not an image", secured_filename
        return False, "Incorrect file extension", secured_filename

    @staticmethod
    def check_mime_type(stream: BytesIO) -> bool:
        """Проверка MIME-типа, чтобы избежать загрузки вредоносного кода"""

        # Проверка
        return imghdr.what(stream)
