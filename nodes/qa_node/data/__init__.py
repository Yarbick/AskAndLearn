"""Инициализация менеджера БД для управления данными через ORM"""

# Работа с файлами и путями
from os.path import dirname

# Работа с ORM
from sqlalchemy.orm import declarative_base
from shared_orm.manage import DatabaseManager

# Создание менеджера для БД
db_url = f"sqlite:///{dirname(__file__)}/databases/qa.db?check_same_thread=False"
db_declarative_base = declarative_base()  # Декларативная база для определения других моделей
db_manager = DatabaseManager(db_url, db_declarative_base)

# Загрузка моделей БД
from .models import __all_models

# Обнаружение всех таблиц и моделей
db_manager.create_tables()
