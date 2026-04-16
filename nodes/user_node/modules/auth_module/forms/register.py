"""Форма регистрации"""

# Работа с шаблонами
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """Форма регистрации"""

    # Поля
    name = StringField("Name", validators=[DataRequired()])
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    repeat_password = PasswordField("Repeat password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Register")
