"""Парсеры для REST API user"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class UserParsers:
    post_put_parser = reqparse.RequestParser()
    post_put_parser.add_argument("name", type=str, required=True)
    post_put_parser.add_argument("login", type=str, required=True)
    post_put_parser.add_argument("password", type=str, required=True)
    post_put_parser.add_argument("description", type=str, nullable=True)
