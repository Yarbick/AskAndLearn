"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class QuestionParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument("limit", type=int, nullable=True)
    get_list_parser.add_argument("search", type=str, nullable=True)
    get_list_parser.add_argument("search_mode", type=str, nullable=True, choices=("name", "tag", "creator"))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("content", type=str, nullable=True)
    post_parser.add_argument("creator_id", type=int, required=True)
    post_parser.add_argument("tags", type=str, nullable=True, action="append")
    post_parser.add_argument("is_solved", type=bool, required=True)
    post_parser.add_argument("is_closed", type=bool, required=True)
    post_parser.add_argument("image", type=str, nullable=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("name", type=str)
    put_parser.add_argument("content", type=str)
    put_parser.add_argument("creator_id", type=int, nullable=True)
    put_parser.add_argument("tags", type=str, nullable=True, action="append")
    put_parser.add_argument("is_solved", type=bool)
    put_parser.add_argument("is_closed", type=bool)
    put_parser.add_argument("image", type=str, nullable=True)
