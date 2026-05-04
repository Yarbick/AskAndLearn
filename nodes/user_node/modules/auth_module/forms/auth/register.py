"""Форма регистрации"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):
    """Форма регистрации"""

    # Поля
    name = StringField("Name", validators=[DataRequired(), Length(max=16)])
    login = StringField("Login", validators=[DataRequired(), Length(max=32)])
    password = PasswordField("Password", validators=[DataRequired()])
    repeat_password = PasswordField("Repeat password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Register")
