"""ORM модель пользователя"""

# Работа с пользователем
from app.app import login_manager

# Безопасность
from werkzeug.security import generate_password_hash, check_password_hash

# Работа с ORM
import sqlalchemy as sa
import sqlalchemy.orm as orm
from .. import db_manager
# "Примеси" для модели
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin, login_user

# Связь с другими моделями
from .friendship import Friendship

# Работа с кешем
from cache.cacher import CacheManager


class User(UserMixin, SerializerMixin, db_manager.declarative_base):
    """ORM модель пользователя"""

    # Название
    __tablename__ = "user"

    # Поля
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column("name", sa.String, nullable=False)
    login = sa.Column("login", sa.String, nullable=False, unique=True)
    password = sa.Column("password", sa.String, nullable=False)
    description = sa.Column("description", sa.String, nullable=True)
    icon = sa.Column("icon", sa.String, nullable=True)

    # Связь с моделями
    friendships_as_user = orm.relationship(
        "Friendship",
        foreign_keys=[Friendship.user_id],
        back_populates="user"
    )
    friendships_as_friend = orm.relationship(
        "Friendship",
        foreign_keys=[Friendship.friend_id],
        back_populates="friend"
    )

    # Методы проверки паролей
    def set_password(self, password: str) -> None:
        """Изменение пароля"""

        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля"""

        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """Загрузка пользователя по ID"""

    with db_manager.create_session() as db_session:
        return db_session.get(User, int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    """Загрузка пользователя по токену авторизации"""

    token: str = request.headers.get("Auth-Token")
    if token:
        # Получение ID по токену из кеша
        user_id: int | None = CacheManager.get(token)

        if user_id:
            return load_user(str(user_id))
    return None
