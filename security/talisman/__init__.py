"""Защита через Flask-Talisman"""

# Работа с фреймворком
from flask import Flask

# Настройки приложения
from app.config import Config

# Безопасность
from flask_talisman import Talisman

# CSP настройки
csp_config: dict = {
    "default-src": ["\'self\'"],
    "script-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
    ],
    "style-src": [
        "\'self\'",
        "\'unsafe-inline\'",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
    ],
    "img-src": ["\'self\'", "data:"],
    "frame-ancestors": ["\'none\'"],
    "base-uri": ["\'self\'"],
    "form-action": ["\'self\'"]
}


def init_talisman(app: Flask) -> Talisman:
    """Инициализация талисмана"""

    # Создание и настройка талисмана
    talisman: Talisman = Talisman(
        app,
        content_security_policy=csp_config,
        force_https=False,  # Отключаем HTTPS для талисмана, так как его предоставляет localhost.run
        frame_options="DENY",
        frame_options_allow_from=None,
        strict_transport_security=True,
        strict_transport_security_max_age=60 * 60 * 24 * 365,
        strict_transport_security_include_subdomains=True,
        session_cookie_secure=Config.SESSION_COOKIE_SECURE,
        session_cookie_http_only=Config.SESSION_COOKIE_HTTPONLY,
        session_cookie_samesite=Config.SESSION_COOKIE_SAMESITE,
        x_content_type_options=True,
        x_xss_protection=True
    )

    return talisman
