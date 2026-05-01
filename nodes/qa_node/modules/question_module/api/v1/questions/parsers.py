"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class QuestionParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument("limit", type=int)
    get_list_parser.add_argument("search", type=str)
    get_list_parser.add_argument("search_mode", type=str, choices=("name", "tag", "creator"))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("content", type=str)
    post_parser.add_argument("creator_id", type=int, required=True)
    post_parser.add_argument("tags", type=str)
    post_parser.add_argument("image", type=str)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("name", type=str)
    put_parser.add_argument("content", type=str)
    put_parser.add_argument("tags", type=str)
    put_parser.add_argument("is_solved", type=bool)
    put_parser.add_argument("is_closed", type=bool)
    put_parser.add_argument("image", type=str)

    patch_delete_creator_relationship = reqparse.RequestParser()
    patch_delete_creator_relationship.add_argument("creator_id", type=int, required=True)
