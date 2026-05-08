"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
import requests
from flask_restful import Resource

# Безопасность
from security.rate_limiter import api_route_limits
from security.xss import clean_html

# Парсеры
from .parsers import QuestionParsers

# Валидаторы
from .validators import QuestionAborts, QuestionValidators

# Работа с ORM
from sqlalchemy import desc as sa_desc
import sqlalchemy.orm as orm
from nodes.qa_node import db_manager
from nodes.qa_node.data.models.question import Question
from nodes.qa_node.data.models.tag import Tag


class QuestionResource(Resource):
    """Ресурс одного вопроса"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self, question_id: int) -> requests.Response:
        """GET запрос для получения данных о вопросе"""

        # Получение вопроса из БД
        with db_manager.create_session() as db_session:
            question: Question | None = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)

            # Вывод результата
            return jsonify({"question": question.to_dict(only=[
                "id", "name", "content", "creator_id", "is_solved", "is_closed", "tags.name", "image", "date_added"
            ])})

    def put(self, question_id: int) -> requests.Response:
        """PUT запрос для изменения вопроса"""

        # Получение данных из парсера
        parser_data: dict = clean_html(QuestionParsers.put_parser.parse_args())
        tags: list | None = None if parser_data.get("tags", None) is None else parser_data.pop("tags", "").split(", ")

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question | None = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)
            if not parser_data["is_closed"] is False: QuestionValidators.is_question_closed(question)

            # Изменение вопроса
            for field_name, value in parser_data.items():
                if value is not None: setattr(question, field_name, value)

            # Сохранение изменений
            db_session.commit()

            # Изменение тегов
            if tags is not None:
                # Сохранение тегов для проверки
                tags_to_check: list[Tag] = question.tags.copy()

                # Удаление старых тегов
                question.tags.clear()

                # Создание новых тегов
                for tag_name in set(tags):
                    if tag_name:
                        # Получение тега из БД
                        tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                        # Создание тега, если его не существует
                        if not tag:
                            tag: Tag = Tag(name=tag_name)
                            db_session.add(tag)

                        # Привязка тега к вопросу
                        question.tags.append(tag)

                # Сохранение изменений
                db_session.commit()

                # Удаление тегов, которые не используются в других вопросах
                for tag in tags_to_check:
                    if not tag.questions:
                        db_session.delete(tag)

                # Сохранение изменений
                db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, question_id: int) -> requests.Response:
        """DELETE запрос для удаления вопроса"""

        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question | None = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)

            # Сохранение тегов для проверки
            tags_to_check: list[Tag] = question.tags.copy()

            # Удаление комментариев под вопросом
            for comment in question.comments:
                db_session.delete(comment)

            # Удаление вопроса из избранных у пользователей
            for favorite in question.favorites:
                db_session.delete(favorite)

            # Удаление вопроса
            db_session.delete(question)
            db_session.commit()

            # Удаление тегов, которые не используются в других вопросах
            for tag in tags_to_check:
                if not tag.questions:
                    db_session.delete(tag)

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class QuestionListResource(Resource):
    """Ресурс списка вопросов"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self) -> requests.Response:
        """GET запрос для получения данных о вопросах"""

        def get_by_limit(query: orm.Query[Question], limit: int | None):
            """Получение вопросов с учётом лимита"""

            if limit is not None:
                return query.order_by(sa_desc(Question.date_added)).limit(limit).all()
            return query.all()

        # Получение данных из парсера
        parser_data: dict = clean_html(QuestionParsers.get_list_parser.parse_args())
        limit: int | None = parser_data.get("limit", None)

        # Получение вопросов из БД
        with db_manager.create_session() as db_session:
            if parser_data["filter"]:  # С фильтром
                if not parser_data["filter_mode"] or parser_data["filter_mode"] == "name":  # Фильтр по имени
                    question_name: str = parser_data["filter"]
                    query: orm.Query[Question] = db_session.query(Question).filter(
                        Question.name.ilike(f"%{question_name}%")
                    )

                    # Получение вопросов с учётом лимита
                    questions: list[Question] = get_by_limit(query, limit)
                elif parser_data["filter_mode"] == "tag":  # Фильтр по тегу
                    # Поиск подходящего тега
                    tag_name: str = parser_data["filter"]
                    tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                    questions: list[Question] = []
                    if tag:
                        # Получение вопросов с учётом лимита
                        questions: list[Question] = tag.questions if limit is None else tag.questions[:limit]
                elif parser_data["filter_mode"] == "creator":  # Фильтр по создателю
                    creator_id: int = int(parser_data["filter"])
                    query: orm.Query[Question] = db_session.query(Question).filter(
                        Question.creator_id == creator_id
                    )

                    # Получение вопросов с учётом лимита
                    questions: list[Question] = get_by_limit(query, limit)
            else:  # Без фильтра
                query: orm.Query[Question] = db_session.query(Question)

                # Получение вопросов с учётом лимита
                questions: list[Question] = get_by_limit(query, limit)

            # Вывод результата
            return jsonify(
                {"questions": [question.to_dict(only=["id", "name", "tags.name"]) for question in questions]}
            )

    def post(self) -> requests.Response:
        """POST запрос для создания вопроса"""

        # Получение данных из парсера
        parser_data: dict = clean_html(QuestionParsers.post_parser.parse_args())
        tags: list | None = None if parser_data.get("tags", None) is None else parser_data.pop("tags", "").split(", ")

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(Question).filter(
                    Question.name == parser_data["name"], Question.creator_id == parser_data["creator_id"]
            ).first(): QuestionAborts.already_exists()

            # Создание вопроса
            question: Question = Question()
            for field_name, value in parser_data.items():
                setattr(question, field_name, value)
            # Проверки
            QuestionValidators.is_available(question)

            # Добавление объекта в БД
            db_session.add(question)
            db_session.commit()

            # Добавление тегов
            if tags is not None:
                for tag_name in set(tags):
                    if tag_name:
                        # Получение тега из БД
                        tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                        # Создание тега, если его не существует
                        if not tag:
                            tag: Tag = Tag(name=tag_name)
                            db_session.add(tag)

                        # Привязка тега к вопросу
                        question.tags.append(tag)

                # Сохранение изменений
                db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": question.id}), 201)

    def patch(self) -> requests.Response:
        """PATCH запрос для удаления связи вопросов с автором"""

        # Получение данных из парсера
        creator_id: int = clean_html(QuestionParsers.patch_delete_creator_relationship.parse_args())["creator_id"]

        # Удаление связи вопросов с автором в БД
        with db_manager.create_session() as db_session:
            # Получение вопросов из БД
            questions: list[Question] = db_session.query(Question).filter(Question.creator_id == creator_id).all()
            # Проверки
            if questions: QuestionValidators.is_available(questions[0])

            # Изменение вопросов (замена ID автора на None)
            for question in questions:
                question.creator_id = None

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})
