"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import QuestionParsers

# Валидаторы
from .validators import QuestionAborts, QuestionValidators

# Работа с ORM
from qa_node import db_manager
from qa_node.data.models.question import Question
from qa_node.data.models.tag import Tag


class QuestionResource(Resource):
    """Ресурс одного вопроса"""

    def get(self, question_id: int):
        # Получение вопроса из БД
        with db_manager.create_session() as db_session:
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)

            # Вывод результата
            return jsonify({"question": question.to_dict(only=[
                "id", "name", "content", "creator_id", "is_solved", "is_closed", "tags.name", "image"
            ])})

    def put(self, question_id: int):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.put_parser.parse_args()
        tags: list = question_data.pop("tags", None)

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)

            # Изменение вопроса
            for field_name, value in question_data.items():
                if value is not None: setattr(question, field_name, value)

            # Сохранение изменений
            db_session.commit()

            # Изменение тегов
            if tags is not None:
                # Сохраняем теги для проверки
                tags_to_check: list[Tag] = question.tags.copy()

                # Удаление старых тегов
                question.tags.clear()

                # Создание новых тегов
                for tag_name in tags:
                    # Получение тега из БД
                    tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                    # Создание тега, если его не существует
                    if not tag:
                        tag = Tag(name=tag_name)
                        db_session.add(tag)

                    # Привязка тега к вопросу
                    question.tags.append(tag)
                db_session.commit()

                # Удаление тегов, которые не используются в других вопросах
                for tag in tags_to_check:
                    if not tag.questions:
                        db_session.delete(tag)
                db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, question_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)

            # Сохранение тегов для проверки
            tags_to_check: list[Tag] = question.tags.copy()

            # Удаление вопроса
            db_session.delete(question)
            db_session.commit()

            # Удаление тегов, которые не используются в других вопросах
            for tag in tags_to_check:
                if not tag.questions:
                    db_session.delete(tag)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class QuestionListResource(Resource):
    """Ресурс списка вопросов"""

    def get(self):
        # Получение данных из парсера
        filter_params = QuestionParsers.get_list_parser.parse_args()

        # Получение вопросов из БД
        with db_manager.create_session() as db_session:
            if filter_params["search"]:
                questions: list[Question] = db_session.query(Question).filter(
                    Question.name.ilike(f"%{filter_params["search"]}%")
                ).all()
            else:
                questions: list[Question] = db_session.query(Question).all()

            # Вывод результата
            return jsonify({"questions": [question.to_dict(only=["id", "name"]) for question in questions]})

    def post(self):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.post_parser.parse_args()
        tags: list = question_data.pop("tags", None)

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(Question).filter(
                    Question.name == question_data["name"], Question.creator_id == question_data["creator_id"]
            ).first(): QuestionAborts.already_exists()

            # Создание вопроса
            question = Question()
            for field_name, value in question_data.items():
                setattr(question, field_name, value)

            # Добавление объекта в БД
            db_session.add(question)
            db_session.commit()

            # Добавление тегов
            if tags is not None:
                for tag_name in tags:
                    # Получение тега из БД
                    tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                    # Создание тега, если его не существует
                    if not tag:
                        tag = Tag(name=tag_name)
                        db_session.add(tag)

                    # Привязка тега к вопросу
                    question.tags.append(tag)
                db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": question.id}), 201)
