"""Модель вопроса"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin

# Работа с временем
from datetime import datetime


class Question(SerializerMixin, db_manager.declarative_base):
    """Модель вопроса"""

    # Название
    __tablename__ = "question"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)
    content = sa.Column("content", sa.String, nullable=True)
    creator_id = sa.Column("creator_id", sa.Integer, nullable=True)
    is_solved = sa.Column("is_solved", sa.Boolean, default=False, nullable=False)
    is_closed = sa.Column("is_closed", sa.Boolean, default=False, nullable=False)
    image = sa.Column("image", sa.String, nullable=True)
    date_added = sa.Column("date_added", sa.DateTime, default=datetime.now().date(), nullable=False)

    # Связи с моделями
    tags = orm.relationship(
        "Tag",
        secondary="tag_to_question",
        back_populates="questions"
    )
    comments = orm.relationship("Comment", back_populates="question")
