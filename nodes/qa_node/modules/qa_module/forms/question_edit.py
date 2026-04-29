"""Форма редактирования вопроса"""

# Работа с формами
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class QuestionEditForm(FlaskForm):
    """Форма редактирования вопроса"""

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
    submit = SubmitField("Edit question")
