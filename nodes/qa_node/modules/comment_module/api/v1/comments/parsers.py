"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class CommentParsers:
    # Парсер для GET (CommentListResource) запроса
    get_list_parser: reqparse.RequestParser = reqparse.RequestParser()
    get_list_parser.add_argument("sort_mode", type=str, default="new", choices=("new", "old"))
    get_list_parser.add_argument("filter", type=str)
    get_list_parser.add_argument("filter_mode", type=str, choices=("question",))

    # Парсер для POST (CommentListResource) запроса
    post_parser: reqparse.RequestParser = reqparse.RequestParser()
    post_parser.add_argument("content", type=str, required=True)
    post_parser.add_argument("creator_id", type=int, required=True)
    post_parser.add_argument("question_id", type=int, required=True)

    # Парсер для PUT (CommentResource) запроса
    put_parser: reqparse.RequestParser = reqparse.RequestParser()
    put_parser.add_argument("content", type=str)

    # Парсер для PATCH (CommentResource) запроса, который отмечает комментарий "полезным"
    patch_useful_parser: reqparse.RequestParser = reqparse.RequestParser()
    patch_useful_parser.add_argument("is_useful", type=bool)

    # Парсер для PATCH (CommentListResource) запроса, который удаляет связь с пользователем
    patch_delete_creator_relationship: reqparse.RequestParser = reqparse.RequestParser()
    patch_delete_creator_relationship.add_argument("creator_id", type=int, required=True)
