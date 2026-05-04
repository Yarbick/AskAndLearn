"""Создание и настройка приложения"""

# Работа с фреймворком
from flask import Flask

# Работа с пользователем
from flask_login import LoginManager

# Безопасность
from flask_wtf import CSRFProtect

# Настройки приложения
from .config import Config

# Создание и настройка приложения
app: Flask = Flask(
    Config.NAME,
    static_folder=Config.STATIC_FOLDER,
    static_url_path=Config.STATIC_URL_PATH,
    template_folder=Config.TEMPLATE_FOLDER
)
# Установка настроек
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
app.config["SESSION_COOKIE_NAME"] = Config.SESSION_COOKIE_NAME
app.config["SESSION_COOKIE_HTTPONLY"] = Config.SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = Config.SESSION_COOKIE_SAMESITE
app.config["SESSION_REFRESH_EACH_REQUEST"] = Config.SESSION_REFRESH_EACH_REQUEST
app.config["PERMANENT_SESSION_LIFETIME"] = Config.PERMANENT_SESSION_LIFETIME
app.config['WTF_CSRF_ENABLED'] = Config.WTF_CSRF_ENABLED
app.config['WTF_CSRF_CHECK_DEFAULT'] = Config.WTF_CSRF_CHECK_DEFAULT
app.config['WTF_CSRF_HEADERS'] = Config.WTF_CSRF_HEADERS

# Инициализация CSRF-защиты
csrf_protect: CSRFProtect = CSRFProtect(app)

# Создание login-менеджера
login_manager: LoginManager = LoginManager()
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
from nodes.qa_node.modules.favorite_module import bp as favorite_bp, api_bp as favorite_api_bp

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
app.register_blueprint(favorite_bp)
app.register_blueprint(favorite_api_bp)
