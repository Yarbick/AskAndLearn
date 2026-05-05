"""Форма изменения пароля"""

# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class ChangePasswordForm(FlaskForm):
    """Форма изменения пароля"""

    # Поля
    login = StringField("Login", validators=[DataRequired()])
    old_password = PasswordField("Old password", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[DataRequired()])
    repeat_new_password = PasswordField("Repeat new password", validators=[DataRequired()])
    submit = SubmitField("Change password")
