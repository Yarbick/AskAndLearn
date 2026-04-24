"""Модель статусов дружбы"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin


class FriendshipStatus(SerializerMixin, db_manager.declarative_base):
    """Модель статусов дружбы"""

    __tablename__ = "friendship_status"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column("name", sa.String, nullable=False)
