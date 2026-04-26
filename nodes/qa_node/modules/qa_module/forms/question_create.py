"""Форма создания вопроса"""

# Работа с формами
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class QuestionCreateForm(FlaskForm):
    """Форма создания вопроса"""

    # Поля
    name = StringField("Title", validators=[DataRequired()])
    tags = StringField("Tags")
    content = TextAreaField("Content")
    image = FileField(
        "Image",
        validators=[FileAllowed(
            ["png", "webp", "jpeg", "jpg"],
            message="Incorrect file extension. Only .jpg, .jpeg, .png, .webp are supported")
        ]
    )
    submit = SubmitField("Create question")
