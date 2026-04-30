"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class CommentParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument("sort_mode", type=str, default="new", choices=("new", "old"))
    get_list_parser.add_argument("search", type=str)
    get_list_parser.add_argument("search_mode", type=str, choices=("question",))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("content", type=str, required=True)
    post_parser.add_argument("creator_id", type=int, required=True)
    post_parser.add_argument("question_id", type=int, required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("content", type=str)
    put_parser.add_argument("is_useful", type=bool)
