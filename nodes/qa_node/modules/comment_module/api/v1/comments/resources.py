"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import CommentParsers

# Валидаторы
from .validators import CommentAborts, CommentValidators

# Работа с ORM
from sqlalchemy import desc as sa_desc
import sqlalchemy.orm as orm
from qa_node import db_manager
from qa_node.data.models.comment import Comment


class CommentResource(Resource):
    """Ресурс одного комментария"""

    def get(self, comment_id: int):
        # Получение комментария из БД
        with db_manager.create_session() as db_session:
            comment: Comment = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)

            # Вывод результата
            return jsonify({"comment": comment.to_dict(only=[
                "id", "content", "creator_id", "question_id", "is_changed", "is_useful", "date_added"
            ])})

    def put(self, comment_id: int):
        # Получение данных из парсера
        comment_data: dict = CommentParsers.put_parser.parse_args()

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение комментария из БД
            comment: Comment = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)
            CommentValidators.is_available(comment)

            # Изменение комментария
            for field_name, value in comment_data.items():
                if value is not None: setattr(comment, field_name, value)
            comment.is_changed = True

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, comment_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение комментария из БД
            comment: Comment = db_session.get(Comment, comment_id)
            # Проверки
            CommentValidators.is_exists(comment)
            CommentValidators.is_available(comment)

            # Удаление комментария
            db_session.delete(comment)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class CommentListResource(Resource):
    """Ресурс списка комментариев"""

    def get(self):
        # Получение данных из парсера
        params = CommentParsers.get_list_parser.parse_args()

        # Получение комментариев из БД
        with db_manager.create_session() as db_session:
            if params["search"]:  # С фильтром
                if not params["search_mode"] or params["search_mode"] == "question":  # Фильтр по имени
                    question_id: int = int(params["search"])
                    query: orm.Query[Comment] = db_session.query(Comment).filter(Comment.question_id == question_id)
            else:  # Без фильтра
                query: orm.Query[Comment] = db_session.query(Comment)

            # Получение комментариев с учётом сортировки
            if params["sort_mode"] == "new":
                comments: list[Comment] = query.order_by(sa_desc(Comment.date_added)).all()
            else:
                comments: list[Comment] = query.all()

            # Вывод результата
            return jsonify({"comments": [comment.to_dict(only=[
                "id", "content", "creator_id", "question_id", "is_changed", "is_useful", "date_added"
            ]) for comment in comments]})

    def post(self):
        # Получение данных из парсера
        comment_data: dict = CommentParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Создание комментария
            comment = Comment()
            for field_name, value in comment_data.items():
                setattr(comment, field_name, value)

            # Добавление объекта в БД
            db_session.add(comment)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": comment.id}), 201)
