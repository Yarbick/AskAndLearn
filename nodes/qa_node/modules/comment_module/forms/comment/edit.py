"""Форма редактирования комментария"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentEditForm(FlaskForm):
    """Форма редактирования комментария"""

    # Поля
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Edit comment")
