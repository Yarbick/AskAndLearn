"""Форма редактирования профиля"""

# Работа с формами
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ProfileEditForm(FlaskForm):
    """Форма редактирования профиля"""

    # Поля
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    icon = FileField(
        "Icon",
        validators=[FileAllowed(
            ["png", "webp", "jpeg", "jpg"],
            message="Incorrect file extension. Only .jpg, .jpeg, .png, .webp are supported")
        ]
    )
    submit = SubmitField("Save")
