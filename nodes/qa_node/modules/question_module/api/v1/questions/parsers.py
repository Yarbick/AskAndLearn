"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class QuestionParsers:
    # Парсер для GET (QuestionListResource) запроса
    get_list_parser: reqparse.RequestParser = reqparse.RequestParser()
    get_list_parser.add_argument("limit", type=int)
    get_list_parser.add_argument("filter", type=str)
    get_list_parser.add_argument("filter_mode", type=str, choices=("name", "tag", "creator"))

    # Парсер для POST (QuestionListResource) запроса
    post_parser: reqparse.RequestParser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("content", type=str)
    post_parser.add_argument("creator_id", type=int, required=True)
    post_parser.add_argument("tags", type=str)
    post_parser.add_argument("image", type=str)

    # Парсер для PUT (QuestionResource) запроса
    put_parser: reqparse.RequestParser = reqparse.RequestParser()
    put_parser.add_argument("name", type=str)
    put_parser.add_argument("content", type=str)
    put_parser.add_argument("tags", type=str)
    put_parser.add_argument("is_solved", type=bool)
    put_parser.add_argument("is_closed", type=bool)
    put_parser.add_argument("image", type=str)

    # Парсер для PATCH (QuestionListResource) запроса, который удаляет связь с пользователем
    patch_delete_creator_relationship: reqparse.RequestParser = reqparse.RequestParser()
    patch_delete_creator_relationship.add_argument("creator_id", type=int, required=True)
