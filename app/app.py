"""Приложение"""

# Работа с фреймворком
from flask import Flask, json, url_for
from flask_login import LoginManager

# Настройки приложения
from .config import Config

# Создание и настройка приложения
app = Flask(
    "AskAndLearn",
    static_folder=Config.static_folder,
    static_url_path=Config.static_url_path,
    template_folder=Config.template_folder
)
app.config["SECRET_KEY"] = Config.secret_key
app.config["PERMANENT_SESSION_LIFETIME"] = Config.permanent_session_lifetime

# Создание login-менеджера
login_manager = LoginManager()
login_manager.init_app(app)

# Модули приложения
from nodes.user_node.modules.auth_module import bp as auth_bp
from nodes.user_node.modules.user_module import bp as user_bp, api_bp as user_api_bp

# Подключение модулей
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(user_api_bp)


# Временный обработчик для главной страницы
@app.route("/")
def root():
    from flask import render_template
    from flask_login import current_user

    return render_template("base.html", user=current_user)
