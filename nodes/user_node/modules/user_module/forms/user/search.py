"""Форма поиска пользователей"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    """Форма поиска пользователей"""

    # Поля
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")
