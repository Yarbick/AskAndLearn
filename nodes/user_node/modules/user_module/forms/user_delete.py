"""Форма удаления пользователя"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class UserDeleteForm(FlaskForm):
    """Форма удаления пользователя"""

    # Поля
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    accept_deleting = BooleanField("I confirm the deletion of my account", validators=[DataRequired()])
    submit = SubmitField("Delete")
