"""Модель избранных"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin


class Favorite(SerializerMixin, db_manager.declarative_base):
    """Модель избранных"""

    # Название
    __tablename__ = "favorite"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sa.Column("user_id", sa.Integer, nullable=False)
    question_id = sa.Column("question_id", sa.Integer, sa.ForeignKey("question.id"), nullable=False)

    # Связи с моделями
    question = orm.relationship(
        "Question",
        foreign_keys=[question_id],
        back_populates="favorites"
    )
