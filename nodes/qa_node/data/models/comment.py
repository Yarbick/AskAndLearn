"""Модель комментария"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin

# Работа с временем
from datetime import datetime


class Comment(SerializerMixin, db_manager.declarative_base):
    """Модель комментария"""

    # Название
    __tablename__ = "comment"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    content = sa.Column("content", sa.String, nullable=False)
    creator_id = sa.Column("creator_id", sa.Integer, nullable=True)
    question_id = sa.Column("question_id", sa.Integer, sa.ForeignKey("question.id"), nullable=False)
    is_changed = sa.Column("is_changed", sa.Boolean, default=False, nullable=False)
    is_useful = sa.Column("is_useful", sa.Boolean, default=False, nullable=False)
    date_added = sa.Column("date_added", sa.DateTime, default=datetime.now, nullable=False)

    # Связи с моделями
    question = orm.relationship("Question", foreign_keys=[question_id], back_populates="comments")
