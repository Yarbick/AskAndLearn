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
from sqlalchemy import desc as sa_desc
import sqlalchemy.orm as orm
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
                "id", "name", "content", "creator_id", "is_solved", "is_closed", "tags.name", "image", "date_added"
            ])})

    def put(self, question_id: int):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.put_parser.parse_args()
        tags: list = None if question_data.get("tags", None) is None else question_data.pop("tags", "").split(", ")

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение вопроса из БД
            question: Question = db_session.get(Question, question_id)
            # Проверки
            QuestionValidators.is_exists(question)
            QuestionValidators.is_available(question)
            if not question_data["is_closed"] is False:
                QuestionValidators.is_question_closed(question)

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
                    if tag_name:
                        # Получение тега из БД
                        tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                        # Создание тега, если его не существует
                        if not tag:
                            tag: Tag = Tag(name=tag_name)
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
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class QuestionListResource(Resource):
    """Ресурс списка вопросов"""

    def get(self):
        def get_by_limit(query: orm.Query[Question.id], limit: int | None):
            """Получение вопросов с учётом лимита"""

            if limit is not None:
                return query.order_by(sa_desc(Question.date_added)).limit(limit).all()
            return query.all()

        # Получение данных из парсера
        params = QuestionParsers.get_list_parser.parse_args()
        limit = params["limit"]

        # Получение вопросов из БД
        with db_manager.create_session() as db_session:
            if params["search"]:  # С фильтром
                if not params["search_mode"] or params["search_mode"] == "name":  # Фильтр по имени
                    question_name: str = params["search"]
                    query: orm.Query[Question] = db_session.query(Question).filter(
                        Question.name.ilike(f"%{question_name}%")
                    )

                    # Получение вопросов с учётом лимита
                    questions: list[Question] = get_by_limit(query, limit)
                elif params["search_mode"] == "tag":  # Фильтр по тегу
                    # Поиск подходящего тега
                    tag_name: str = params["search"]
                    tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                    if tag:
                        # Получение вопросов с учётом лимита
                        questions: list[Question] = tag.questions if limit is None else tag.questions[:limit]
                    else:
                        questions: list = []
                elif params["search_mode"] == "creator":  # Фильтр по создателю
                    creator_id: int = int(params["search"])
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

    def post(self):
        # Получение данных из парсера
        question_data: dict = QuestionParsers.post_parser.parse_args()
        tags: list = None if question_data.get("tags", None) is None else question_data.pop("tags", "").split(", ")

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
            # Проверки
            QuestionValidators.is_available(question)

            # Добавление объекта в БД
            db_session.add(question)
            db_session.commit()

            # Добавление тегов
            if tags is not None:
                for tag_name in tags:
                    if tag_name:
                        # Получение тега из БД
                        tag: Tag = db_session.query(Tag).filter(Tag.name == tag_name).first()

                        # Создание тега, если его не существует
                        if not tag:
                            tag: Tag = Tag(name=tag_name)
                            db_session.add(tag)

                        # Привязка тега к вопросу
                        question.tags.append(tag)
                db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": question.id}), 201)

    def patch(self):
        """Удаление связи вопросов с автором"""

        # Получение данных из парсера
        creator_id: int = QuestionParsers.patch_delete_creator_relationship.parse_args()["creator_id"]

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
