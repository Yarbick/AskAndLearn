"""Парсеры для REST API ресурса"""

# Работа с REST API
from flask_restful import reqparse

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class FriendshipParsers:
    get_list_parser = reqparse.RequestParser()
    get_list_parser.add_argument(
        "search", type=str, nullable=True, action="append",
        choices=("accepted", "pending", "blocked"), default=["accepted", "pending", "blocked"]
    )
    get_list_parser.add_argument(
        "search_mode", type=str, nullable=True, choices=("status",)
    )

    post_parser = reqparse.RequestParser()
    post_parser.add_argument("friend_id", type=int, required=True)
    post_parser.add_argument("status", type=str, required=True, choices=("accepted", "pending", "blocked"))

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("status", type=str, nullable=True, choices=("accepted", "pending", "blocked"))
