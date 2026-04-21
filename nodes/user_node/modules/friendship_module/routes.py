"""Обработчики маршрутов модуля Friendship"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

# Безопасность
from security.csrf import create_csrf_request_session

# Подключение к модулю
from .blueprint import bp

# Настройки модуля
from .config import Config

# Работа с REST API
import requests

# Формы
from .forms.profile_edit import ProfileEditForm
from .forms.user_delete import UserDeleteForm
