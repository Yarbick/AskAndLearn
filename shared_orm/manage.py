"""Управление БД через ORM"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm


class DatabaseManager:
    """Класс для работы с БД через ORM"""

    def __init__(self, database_url: str, declarative_base: orm.DeclarativeBase):
        self.declarative_base = declarative_base  # Декларативная база для определения моделей
        self.engine: sa.Engine = sa.create_engine(database_url)  # Движок
        self.session_maker: orm.sessionmaker = orm.sessionmaker(bind=self.engine)  # Фабрика сессий

    def create_tables(self) -> None:
        """Обнаружение всех моделей и таблиц"""

        self.declarative_base.metadata.create_all(bind=self.engine)

    def create_session(self) -> orm.Session:
        """Создание сессии"""

        return self.session_maker()
