"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
import requests
from flask_restful import Resource

# Безопасность
from security.rate_limiter import api_route_limits

# Парсеры
from .parsers import CommentParsers

# Валидаторы
from .validators import CommentValidators

# Работа с ORM
from sqlalchemy import desc as sa_desc
import sqlalchemy.orm as orm
from nodes.qa_node import db_manager
from nodes.qa_node.data.models.comment import Comment
from nodes.qa_node.data.models.question import Question


class CommentResource(Resource):
    """Ресурс одного комментария"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self, comment_id: int) -> requests.Response:
        """GET запрос для получения данных о комментарии"""

        # Получение комментария из БД
        with db_manager.create_session() as db_session:
            comment: Comment | None = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)

            # Вывод результата
            return jsonify({"comment": comment.to_dict(only=[
                "id", "content", "creator_id", "question_id", "is_changed", "is_useful", "date_added"
            ])})

    def put(self, comment_id: int) -> requests.Response:
        """PUT запрос для изменения комментария"""

        # Получение данных из парсера
        parser_data: dict = CommentParsers.put_parser.parse_args()

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение комментария из БД
            comment: Comment | None = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)
            CommentValidators.is_available(comment)
            CommentValidators.is_question_closed(comment)

            # Изменение комментария
            for field_name, value in parser_data.items():
                if value is not None: setattr(comment, field_name, value)
            comment.is_changed = True

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, comment_id: int) -> requests.Response:
        """DELETE запрос для удаления комментария"""

        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение комментария из БД
            comment: Comment | None = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)
            CommentValidators.is_available(comment)
            CommentValidators.is_question_closed(comment)

            # Удаление комментария
            db_session.delete(comment)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def patch(self, comment_id: int) -> requests.Response:
        """PATCH запрос для изменения состояния is_useful"""

        # Получение данных из парсера
        comment_data: dict = CommentParsers.patch_useful_parser.parse_args()

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение комментария из БД
            comment: Comment | None = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)
            CommentValidators.is_question_author(comment)
            CommentValidators.is_question_closed(comment)

            # Изменение состояния is_useful
            comment.is_useful = comment_data["is_useful"]

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class CommentListResource(Resource):
    """Ресурс списка комментариев"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self) -> requests.Response:
        """GET запрос для получения данных о комментариях"""

        # Получение данных из парсера
        parser_data = CommentParsers.get_list_parser.parse_args()

        # Получение комментариев из БД
        with db_manager.create_session() as db_session:
            if parser_data["filter"]:  # С фильтром
                if not parser_data["filter_mode"] or parser_data["filter_mode"] == "question":  # Фильтр по имени
                    question_id: int = int(parser_data["filter"])
                    query: orm.Query[Comment] = db_session.query(Comment).filter(Comment.question_id == question_id)
            else:  # Без фильтра
                query: orm.Query[Comment] = db_session.query(Comment)

            # Получение комментариев с учётом сортировки
            if parser_data["sort_mode"] == "new":
                comments: list[Comment] = query.order_by(sa_desc(Comment.date_added)).all()
            else:
                comments: list[Comment] = query.all()

            # Вывод результата
            return jsonify({"comments": [comment.to_dict(only=[
                "id", "content", "creator_id", "question_id", "is_changed", "is_useful", "date_added"
            ]) for comment in comments]})

    def post(self) -> requests.Response:
        """POST запрос для создания комментария"""

        # Получение данных из парсера
        parser_data: dict = CommentParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Создание комментария
            comment: Comment = Comment()
            for field_name, value in parser_data.items():
                setattr(comment, field_name, value)
            # Проверки
            question: Question | None = db_session.get(Question, comment.question_id)
            CommentValidators.is_exists(question)
            CommentValidators.is_question_closed(question)
            CommentValidators.is_available(comment)

            # Добавление объекта в БД
            db_session.add(comment)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": comment.id}), 201)

    def patch(self) -> requests.Response:
        """PATCH запрос для удаления связи с создателем"""

        # Получение данных из парсера
        creator_id: int = CommentParsers.patch_delete_creator_relationship.parse_args()["creator_id"]

        # Удаление связи комментариев с создателем в БД
        with db_manager.create_session() as db_session:
            # Получение комментариев из БД
            comments: list[Comment] = db_session.query(Comment).filter(Comment.creator_id == creator_id).all()
            # Проверки
            if comments: CommentValidators.is_available(comments[0])

            # Изменение комментариев (замена ID автора на None)
            for comment in comments:
                comment.creator_id = None

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})
