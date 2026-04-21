"""Модель дружбы"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin


class Friendship(SerializerMixin, db_manager.declarative_base):
    """Модель дружбы (промежуточная между моделями User)"""

    __tablename__ = "friendship"

    # Поля
    user_id = sa.Column("user", sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    friend_id = sa.Column("friend", sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    status = sa.Column("status", sa.String, sa.ForeignKey("users.id"), nullable=False)

    # Связь с моделями
    user = orm.relationship("User", foreign_keys=[user_id])
    friend = orm.relationship("User", foreign_keys=[friend_id])
