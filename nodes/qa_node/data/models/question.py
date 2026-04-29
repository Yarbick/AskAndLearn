"""Модель вопроса"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin


class Question(SerializerMixin, db_manager.declarative_base):
    """Модель вопроса"""

    # Название
    __tablename__ = "question"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)
    content = sa.Column("content", sa.String, nullable=True)
    creator_id = sa.Column("creator_id", sa.Integer, nullable=True)
    is_solved = sa.Column("is_solved", sa.Boolean, nullable=False)
    is_closed = sa.Column("is_closed", sa.Boolean, nullable=False)
    image = sa.Column("image", sa.String, nullable=True)

    # Связи с моделями
    tags = orm.relationship(
        "Tag",
        secondary="tag_to_question",
        back_populates="questions"
    )
