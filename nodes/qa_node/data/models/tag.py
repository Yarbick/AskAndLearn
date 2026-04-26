"""Модель тега вопроса"""

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin

# Промежуточная таблица между тегами и вопросами
tag_to_question = sa.Table(
    "tag_to_question",
    db_manager.declarative_base.metadata,
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tag.id"), nullable=False),
    sa.Column("question_id", sa.Integer, sa.ForeignKey("question.id"), nullable=False)
)


class Tag(SerializerMixin, db_manager.declarative_base):
    """Модель тега вопроса"""

    # Название
    __tablename__ = "tag"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)

    # Связи с моделями
    questions = orm.relationship(
        "Question",
        secondary="tag_to_question",
        back_populates="tags"
    )
