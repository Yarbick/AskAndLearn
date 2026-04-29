"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class UserParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument("search", type=str, nullable=True)
    get_list_parser.add_argument("search_mode", type=str, nullable=True, choices=("name-login",))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("name", type=str, required=True)
    post_parser.add_argument("login", type=str, required=True)
    post_parser.add_argument("password", type=str, required=True)
    post_parser.add_argument("description", type=str, nullable=True)
    post_parser.add_argument("icon", type=str, nullable=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("name", type=str)
    put_parser.add_argument("login", type=str)
    put_parser.add_argument("password", type=str)
    put_parser.add_argument("description", type=str, nullable=True)
    put_parser.add_argument("icon", type=str, nullable=True)
