"""Приложение"""

# Работа с фреймворком
from flask import Flask, json, url_for
from flask_login import LoginManager

# Настройки приложения
from .config import Config

# Работа с формами
from flask_wtf import CSRFProtect

# Создание и настройка приложения
app = Flask(
    "AskAndLearn",
    static_folder=Config.static_folder,
    static_url_path=Config.static_url_path,
    template_folder=Config.template_folder
)
app.config["SECRET_KEY"] = Config.secret_key
app.config["MAX_CONTENT_LENGTH"] = Config.max_content_length
app.config["SESSION_COOKIE_NAME"] = Config.session_cookie_name
app.config["SESSION_COOKIE_HTTPONLY"] = Config.session_cookie_httponly
app.config["SESSION_COOKIE_SAMESITE"] = Config.session_cookie_samesite
app.config["SESSION_REFRESH_EACH_REQUEST"] = Config.session_refresh_each_request
app.config["PERMANENT_SESSION_LIFETIME"] = Config.permanent_session_lifetime
app.config['WTF_CSRF_ENABLED'] = Config.wtf_csrf_enabled
app.config['WTF_CSRF_CHECK_DEFAULT'] = Config.wtf_csrf_check_default
app.config['WTF_CSRF_HEADERS'] = Config.wtf_csrf_headers

# Инициализация CSRF-защиты
csrf_protect = CSRFProtect(app)

# Создание login-менеджера
login_manager = LoginManager()
login_manager.init_app(app)

# Модули приложения
# Узел welcome_node
from nodes.welcome_node.modules.welcome_module import bp as welcome_bp
# Узел user_node
from nodes.user_node.modules.auth_module import bp as auth_bp
from nodes.user_node.modules.user_module import bp as user_bp, api_bp as user_api_bp
from nodes.user_node.modules.friendship_module import bp as friendship_bp, api_bp as friendship_api_bp
# Узел qa_node
from nodes.qa_node.modules.question_module import bp as question_bp, api_bp as question_api_bp
from nodes.qa_node.modules.comment_module import bp as comment_bp, api_bp as comment_api_bp

# Регистрация модулей
# Узел welcome_node
app.register_blueprint(welcome_bp)
# Узел user_node
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(user_api_bp)
app.register_blueprint(friendship_bp)
app.register_blueprint(friendship_api_bp)
# Узел qa_node
app.register_blueprint(question_bp)
app.register_blueprint(question_api_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(comment_api_bp)
