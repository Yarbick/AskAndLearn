"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class FriendshipParsers:
    # Парсер для GET (FriendshipListResource) запроса
    get_list_parser: reqparse.RequestParser = reqparse.RequestParser()
    get_list_parser.add_argument("filter", type=str)
    get_list_parser.add_argument("filter_mode", type=str, choices=("status",))

    # Парсер для POST (FriendshipListResource) запроса
    post_parser: reqparse.RequestParser = reqparse.RequestParser()
    post_parser.add_argument("friend_id", type=int, required=True)
    post_parser.add_argument("status", type=str, required=True, choices=("accepted", "pending", "blocked"))

    # Парсер для PUT (FriendshipResource) запроса
    put_parser: reqparse.RequestParser = reqparse.RequestParser()
    put_parser.add_argument("status", type=str, required=True, choices=("accepted", "pending", "blocked"))
