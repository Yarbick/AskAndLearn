"""Форма создания комментария"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommentCreateForm(FlaskForm):
    """Форма создания комментария"""

    # Поля
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post comment")
