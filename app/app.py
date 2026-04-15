"""Приложение"""

# Работа с фреймворком
from flask import Flask, json
from flask_login import LoginManager

# Настройки приложения
from .config import Config

# Создание и настройка приложения
app = Flask(
    "AskAndLearn",
    static_folder=Config.static_folder,
    template_folder=Config.template_folder
)
app.config["SECRET_KEY"] = Config.secret_key
app.config["PERMANENT_SESSION_LIFETIME"] = Config.permanent_session_lifetime

# Создание login-менеджера
login_manager = LoginManager()
login_manager.init_app(app)

# Модули приложения
from nodes.user_node.modules.auth_module import bp as auth_bp

# Подключение модулей
app.register_blueprint(auth_bp)
