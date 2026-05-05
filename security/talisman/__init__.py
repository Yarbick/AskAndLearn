"""Защита через Flask-Talisman"""

# Работа с фреймворком
from flask import Flask

# Безопасность
from flask_talisman import Talisman

# CSP настройки
csp_config: dict = {
    "default-src": ["\'self\'"],
    "script-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
    ],
    "style-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
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
        force_https=False,
        frame_options="DENY",
        frame_options_allow_from=None,
        strict_transport_security=True,
        strict_transport_security_max_age=60 * 60 * 24 * 365,
        strict_transport_security_include_subdomains=True,
        session_cookie_secure=False,
        session_cookie_http_only=True,
        session_cookie_samesite="Lax",
        x_content_type_options=True,
        x_xss_protection=True
    )

    return talisman
