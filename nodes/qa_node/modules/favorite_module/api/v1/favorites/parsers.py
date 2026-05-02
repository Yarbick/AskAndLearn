"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class FavoriteParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument("search", type=str)
    get_list_parser.add_argument("search_mode", type=str, choices=("user", "question"))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("user_id", type=int, required=True)
    post_parser.add_argument("question_id", type=int, required=True)
