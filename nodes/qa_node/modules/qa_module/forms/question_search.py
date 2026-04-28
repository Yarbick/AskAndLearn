"""Форма поиска вопросов"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class QuestionSearchForm(FlaskForm):
    """Форма поиска вопросов"""

    # Поля
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")
