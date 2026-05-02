"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import FavoriteParsers

# Валидаторы
from .validators import FavoriteAborts, FavoriteValidators

# Работа с ORM
from qa_node import db_manager
from qa_node.data.models.favorite import Favorite
from qa_node.data.models.question import Question


class FavoriteResource(Resource):
    """Ресурс одного избранного вопроса"""

    def get(self, favorite_id: int):
        # Получение избранного вопроса из БД
        with db_manager.create_session() as db_session:
            favorite: Favorite = db_session.get(Favorite, favorite_id)
            # Проверки
            FavoriteValidators.is_exists(favorite)

            # Вывод результата
            return jsonify({"favorite": favorite.to_dict(only=[
                "id", "question.id", "question.name", "question.tags.name", "user_id"
            ])})

    def delete(self, favorite_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение избранного вопроса из БД
            favorite: Favorite = db_session.get(Favorite, favorite_id)
            # Проверки
            FavoriteValidators.is_exists(favorite)
            FavoriteValidators.is_available(favorite)

            # Удаление вопроса из избранных пользователя
            db_session.delete(favorite)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class FavoriteListResource(Resource):
    """Ресурс списка избранных вопросов"""

    def get(self):
        # Получение данных из парсера
        params = FavoriteParsers.get_list_parser.parse_args()

        # Получение избранных вопросов из БД
        with db_manager.create_session() as db_session:
            if params["search"]:  # С фильтром
                if not params["search_mode"] or params["search_mode"] == "user":  # Фильтр по пользователю
                    user_id: int = int(params["search"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.user_id == user_id
                    ).all()
                elif params["search_mode"] == "question":  # Фильтр по вопросу
                    question_id: int = int(params["search"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.question_id == question_id
                    ).all()
            else:  # Без фильтра
                favorites: list[Favorite] = db_session.query(Favorite).all()

            # Вывод результата
            return jsonify({"favorites": [
                favorite.to_dict(only=["id", "question.id", "question.name", "question.tags.name", "user_id"])
                for favorite in favorites
            ]})

    def post(self):
        # Получение данных из парсера
        favorite_data: dict = FavoriteParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(Favorite).filter(
                    Favorite.user_id == favorite_data["user_id"], Favorite.question_id == favorite_data["question_id"]
            ).first(): FavoriteAborts.already_exists()

            # Добавление вопроса в избранные пользователя
            favorite: Favorite = Favorite()
            for field_name, value in favorite_data.items():
                setattr(favorite, field_name, value)
            # Проверки
            FavoriteValidators.is_available(favorite)

            # Добавление объекта в БД
            db_session.add(favorite)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": favorite.id}), 201)

    def delete(self):
        # Получение данных из парсера
        params = FavoriteParsers.get_list_parser.parse_args()

        # Удаление избранных вопросов из БД
        with db_manager.create_session() as db_session:
            # Получение избранных вопросов
            if params["search"]:  # С фильтром
                if not params["search_mode"] or params["search_mode"] == "user":  # Фильтр по пользователю
                    user_id: int = int(params["search"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.user_id == user_id
                    ).all()
                elif params["search_mode"] == "question":  # Фильтр по вопросу
                    question_id: int = int(params["search"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.question_id == question_id
                    ).all()
            else:  # Без фильтра
                favorites: list[Favorite] = db_session.query(Favorite).all()

            # Удаление избранных вопросов
            for favorite in favorites:
                db_session.delete(favorite)

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})
