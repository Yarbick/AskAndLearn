"""Модель пользователя"""

# Работа с фреймворком
from app.app import login_manager

# Работа с ORM
import sqlalchemy as sa
from .. import db_manager
from werkzeug.security import generate_password_hash, check_password_hash
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin, login_user


class User(UserMixin, SerializerMixin, db_manager.declarative_base):
    """Модель пользователя"""

    # Название
    __tablename__ = "user"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)
    login = sa.Column("login", sa.String, nullable=False, unique=True)
    password = sa.Column("password", sa.String, nullable=False)
    description = sa.Column("description", sa.String, nullable=True)

    def set_password(self, password: str) -> None:
        """Изменение пароля"""

        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля"""

        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """Загрузка пользователя по ID"""

    with db_manager.create_session() as db_session:
        return db_session.get(User, int(user_id))
