"""Модель дружбы"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin


class Friendship(SerializerMixin, db_manager.declarative_base):
    """Модель дружбы"""

    __tablename__ = "friendship"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False)
    friend_id = sa.Column("friend_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False)
    last_changed_by = sa.Column("last_changed_by", sa.Integer, nullable=False)
    status = sa.Column("status", sa.String, nullable=False)

    # Связь с моделями
    user = orm.relationship("User", foreign_keys=[user_id])
    friend = orm.relationship("User", foreign_keys=[friend_id])
