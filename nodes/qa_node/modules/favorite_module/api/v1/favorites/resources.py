"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
import requests
from flask_restful import Resource

# Безопасность
from security.rate_limiter import api_route_limits

# Парсеры
from .parsers import FavoriteParsers

# Валидаторы
from .validators import FavoriteAborts, FavoriteValidators

# Работа с ORM
from nodes.qa_node import db_manager
from nodes.qa_node.data.models.favorite import Favorite
from nodes.qa_node.data.models.question import Question


class FavoriteResource(Resource):
    """Ресурс одного избранного вопроса"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self, favorite_id: int) -> requests.Response:
        """GET запрос для получения данных об избранном вопросе"""

        # Получение избранного вопроса из БД
        with db_manager.create_session() as db_session:
            favorite: Favorite | None = db_session.get(Favorite, favorite_id)
            # Проверки
            FavoriteValidators.is_exists(favorite)

            # Вывод результата
            return jsonify({"favorite": favorite.to_dict(only=[
                "id", "question.id", "question.name", "question.tags.name", "user_id"
            ])})

    def delete(self, favorite_id: int) -> requests.Response:
        """DELETE запрос для удаления вопроса из избранных пользователя"""

        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение избранного вопроса из БД
            favorite: Favorite | None = db_session.get(Favorite, favorite_id)
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

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self) -> requests.Response:
        """GET запрос для получения избранных"""

        # Получение данных из парсера
        parser_params: dict = FavoriteParsers.get_list_parser.parse_args()

        # Получение избранных вопросов из БД
        with db_manager.create_session() as db_session:
            if parser_params["filter"]:  # С фильтром
                if not parser_params["filter_mode"] or parser_params["filter_mode"] == "user":  # Фильтр по пользователю
                    user_id: int = int(parser_params["filter"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.user_id == user_id
                    ).all()
                elif parser_params["filter_mode"] == "question":  # Фильтр по вопросу
                    question_id: int = int(parser_params["filter"])
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

    def post(self) -> requests.Response:
        """POST запрос для добавления вопроса в избранные пользователя"""

        # Получение данных из парсера
        parser_data: dict = FavoriteParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(Favorite).filter(
                    Favorite.user_id == parser_data["user_id"], Favorite.question_id == parser_data["question_id"]
            ).first(): FavoriteAborts.already_exists()

            # Добавление вопроса в избранные пользователя
            favorite: Favorite | None = Favorite()
            for field_name, value in parser_data.items():
                setattr(favorite, field_name, value)
            # Проверки
            question: Question | None = db_session.get(Question, favorite.question_id)
            FavoriteValidators.is_exists(question)
            FavoriteValidators.is_available(favorite)

            # Добавление объекта в БД
            db_session.add(favorite)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": favorite.id}), 201)

    def delete(self) -> requests.Response:
        """DELETE запрос для очистки избранных пользователя"""

        # Получение данных из парсера
        parser_params: dict = FavoriteParsers.get_list_parser.parse_args()

        # Удаление избранных вопросов из БД
        with db_manager.create_session() as db_session:
            # Получение избранных вопросов
            if parser_params["filter"]:  # С фильтром
                if not parser_params["filter_mode"] or parser_params["filter_mode"] == "user":  # Фильтр по пользователю
                    user_id: int = int(parser_params["filter"])
                    favorites: list[Favorite] = db_session.query(Favorite).filter(
                        Favorite.user_id == user_id
                    ).all()
                elif parser_params["filter_mode"] == "question":  # Фильтр по вопросу
                    question_id: int = int(parser_params["filter"])
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
