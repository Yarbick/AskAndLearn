"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class FavoriteParsers:
    # Парсер для GET (FavoriteListResource) запроса
    get_list_parser: reqparse.RequestParser = reqparse.RequestParser()
    get_list_parser.add_argument("filter", type=str)
    get_list_parser.add_argument("filter_mode", type=str, choices=("user", "question"))

    # Парсер для POST (FavoriteListResource) запроса
    post_parser: reqparse.RequestParser = reqparse.RequestParser()
    post_parser.add_argument("user_id", type=int, required=True)
    post_parser.add_argument("question_id", type=int, required=True)
