import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Базовая конфигурация приложения"""
    
    # Секретный ключ для сессий и CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # База данных SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки Flask-Login
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Администратор по умолчанию
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # В продакшене менять!
    
    # Логирование
    LOG_TO_STDOUT = True
    
    # Настройки почты (опционально)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # FAQ Widget Configuration
    FAQ_API_BASE = os.environ.get('FAQ_API_BASE') or 'http://localhost:8000'
