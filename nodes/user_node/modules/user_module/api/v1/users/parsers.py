"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class UserParsers:
    # Парсер для GET (UserListResource) запроса
    get_list_parser: reqparse.RequestParser = reqparse.RequestParser()
    get_list_parser.add_argument("filter", type=str)
    get_list_parser.add_argument("filter_mode", type=str, choices=("name-login",))

    # Парсер для POST (UserListResource) запроса
    post_parser: reqparse.RequestParser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("login", type=str, required=True)
    post_parser.add_argument("password", type=str, required=True)
    post_parser.add_argument("description", type=str)
    post_parser.add_argument("icon", type=str)

    # Парсер для PUT (UserResource) запроса
    put_parser: reqparse.RequestParser = reqparse.RequestParser()
    put_parser.add_argument("name", type=str)
    put_parser.add_argument("password", type=str)
    put_parser.add_argument("description", type=str)
    put_parser.add_argument("icon", type=str)
