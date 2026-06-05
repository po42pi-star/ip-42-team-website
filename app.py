"""
Flask веб-приложение с админ-панелью
Разработано IP-42-Team
"""

import os
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional

from config import Config

# === Инициализация приложения ===
app = Flask(__name__)
app.config.from_object(Config)

# === Расширения ===
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
login_manager.login_message_category = 'info'

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Директория проекта ===
basedir = os.path.abspath(os.path.dirname(__file__))


# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================

class Admin(UserMixin, db.Model):
    """Модель администратора"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Хеширование пароля"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class ContactMessage(db.Model):
    """Модель сообщений из формы обратной связи"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.email}>'


class Case(db.Model):
    """Модель кейсов"""
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(256), default='case_placeholder.jpg')
    technologies = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Case {self.title}>'


# ==================== ФОРМЫ ====================

class ContactForm(FlaskForm):
    """Форма обратной связи"""
    name = StringField('Ваше имя', validators=[
        DataRequired(message='Введите ваше имя'),
        Length(min=2, max=100, message='Имя должно быть от 2 до 100 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Введите корректный email')
    ])
    phone = StringField('Телефон', validators=[
        Optional(),
        Regexp(r'^[\d\s\+\-\(\)]{7,20}$', message='Введите корректный номер телефона')
    ])
    subject = StringField('Тема сообщения', validators=[
        DataRequired(message='Введите тему сообщения'),
        Length(min=5, max=200, message='Тема должна быть от 5 до 200 символов')
    ])
    message = TextAreaField('Сообщение', validators=[
        DataRequired(message='Введите сообщение'),
        Length(min=10, max=5000, message='Сообщение должно быть от 10 до 5000 символов')
    ])
    submit = SubmitField('Отправить')


class LoginForm(FlaskForm):
    """Форма входа для администратора"""
    username = StringField('Логин', validators=[
        DataRequired(message='Введите логин')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    submit = SubmitField('Войти')


# ==================== МЕНЕДЖЕР ПОЛЬЗОВАТЕЛЕЙ ====================

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def create_admin():
    """Создание администратора по умолчанию"""
    admin = Admin.query.filter_by(username=Config.ADMIN_USERNAME).first()
    if not admin:
        admin = Admin(username=Config.ADMIN_USERNAME)
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        logger.info('Администратор по умолчанию создан')
    return admin


def create_default_cases():
    """Создание кейсов по умолчанию"""
    cases_data = [
        {
            'title': 'ИИ-ассистент техподдержки',
            'slug': 'ai-support-assistant',
            'short_description': 'Кастомный ИИ-ассистент для автоматизации технической поддержки и обработки FAQ.',
            'full_description': '''
                <h3>О проекте</h3>
                <p>Разработан кастомный ИИ-ассистент на базе современных NLP-моделей для автоматизации 
                технической поддержки клиентов. Система обрабатывает входящие обращения, классифицирует их 
                и генерирует точные ответы на основе базы знаний компании.</p>
                
                <h3>Реализованный функционал:</h3>
                <ul>
                    <li>Автоматическая обработка технических обращений 24/7</li>
                    <li>Интеллектуальная классификация проблем пользователей</li>
                    <li>Генерация ответов на основе базы знаний (RAG-архитектура)</li>
                    <li>Интеграция с тикет-системой и CRM</li>
                    <li>Аналитика качества ответов и удовлетворённости клиентов</li>
                    <li>Обучение на истории диалогов для улучшения качества</li>
                </ul>
                
                <h3>Технологии:</h3>
                <p>Python, Transformers, FastAPI, PostgreSQL, Redis, Docker</p>
                
                <h3>Результат:</h3>
                <p>Автоматизация 75% обращений в техподдержку, сокращение времени ответа с 6 часов до 30 секунд, 
                повышение удовлетворённости клиентов на 45%.</p>
            ''',
            'image': 'case1.jpg',
            'technologies': 'Python, Transformers, FastAPI, RAG, NLP'
        },
        {
            'title': 'ИИ-ассистент для обработки отзывов',
            'slug': 'ai-review-assistant',
            'short_description': 'Интеллектуальный Telegram-бот для обработки отзывов клиентов, построенный на принципах RAG.',
            'full_description': '''
                <h3>О проекте</h3>
                <p>Создан интеллектуальный Telegram-бот для автоматической обработки и анализа отзывов клиентов. 
                Система использует RAG-архитектуру (Retrieval-Augmented Generation) для генерации персонализированных 
                ответов на основе контекста и истории взаимодействий.</p>
                
                <h3>Реализованный функционал:</h3>
                <ul>
                    <li>Сбор и анализ отзывов из Telegram и других платформ</li>
                    <li>Автоматический анализ тональности (sentiment analysis)</li>
                    <li>Генерация персонализированных ответов на отзывы</li>
                    <li>Выявление ключевых тем и проблем клиентов</li>
                    <li>Интеграция с CRM и системами обратной связи</li>
                    <li>Отчёты и дашборды для менеджеров</li>
                </ul>
                
                <h3>Технологии:</h3>
                <p>Python, aiogram, Transformers, LangChain, PostgreSQL, Redis</p>
                
                <h3>Результат:</h3>
                <p>Обработка 500+ отзывов в день, время ответа сокращено с 4 часов до 5 минут, 
                рост рейтинга компании на 1.5 звезды за 2 месяца.</p>
            ''',
            'image': 'case2.jpg',
            'technologies': 'Python, aiogram, LangChain, RAG, NLP'
        },
        {
            'title': 'ИИ-анализ конкурентной среды и аналитика',
            'slug': 'ai-parser-app',
            'short_description': 'Приложение для анализа конкурентов с помощью ИИ и получения структурированной аналитики.',
            'full_description': '''
                <h3>О проекте</h3>
                <p>Разработано приложение для анализа конкурентов с помощью ИИ (текст, изображения, PDF, парсинг сайтов) и получения структурированной аналитики. Доступны web- и desktop- версии. Решение позволяет отслеживать и извлекать ценную информацию в реальном времени.</p>
                
                <h3>Реализованный функционал:</h3>
                <ul>
                    <li>Анализ текста</li>
                    <li>Анализ изображений</li>
                    <li>Анализ PDF и извлечение текста</li>
                    <li>Парсинг сайтов</li>
                    <li>Генерация отчетов в html, markdown, pdf</li>
                    <li>Экспорт данных в различных форматах (JSON, CSV, PDF)</li>
                </ul>
                
                <h3>Технологии:</h3>
                <p>Python, FastAPI, PyQt6, Selenium, BeautifulSoup4, PyPDF2, Vanilla JSr</p>
                
                <h3>Результат:</h3>
                <p>Автоматический анализ с помощью ИИ 1000+ единиц документов, парсинг 100+ сайтов в день, 
                экономия 20+ часов ручного анализа еженедельно.</p>
            ''',
            'image': 'case3.jpg',
            'technologies': 'Python, FastAPI, PyQt6, Selenium, BeautifulSoup4, PyPDF2, Vanilla JS'
        }
    ]
    
    # Удаляем старые кейсы перед созданием новых
    Case.query.delete()
    
    for case_data in cases_data:
        existing = Case.query.filter_by(slug=case_data['slug']).first()
        if not existing:
            case = Case(**case_data)
            db.session.add(case)
    
    db.session.commit()
    logger.info('Кейсы по умолчанию созданы')


# ==================== МАРШРУТЫ - ОСНОВНЫЕ СТРАНИЦЫ ====================

@app.route('/')
def index():
    """Главная страница"""
    cases = Case.query.limit(3).all()
    return render_template('index.html', cases=cases)


@app.route('/cases')
def cases():
    """Страница со всеми кейсами"""
    all_cases = Case.query.order_by(Case.created_at.desc()).all()
    return render_template('cases.html', cases=all_cases)


@app.route('/case/<slug>')
def case_detail(slug):
    """Детальная страница кейса"""
    case = Case.query.filter_by(slug=slug).first_or_404()
    return render_template('case_detail.html', case=case)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Страница обратной связи"""
    form = ContactForm()
    
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data or '',
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        logger.info(f'Новое сообщение от {form.email.data}')
        flash('Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form)


# ==================== МАРШРУТЫ - АДМИН-ПАНЕЛЬ ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Вход в админ-панель"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=True)
            logger.info(f'Администратор {admin.username} вошел в систему')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        
        flash('Неверный логин или пароль', 'danger')
    
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Выход из админ-панели"""
    logout_user()
    logger.info('Администратор вышел из системы')
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    """Панель администратора - список сообщений"""
    # Статистика
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         messages=recent_messages,
                         total=total_messages,
                         unread=unread_messages)


@app.route('/admin/messages')
@login_required
def admin_messages():
    """Все сообщения"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Отметить сообщение как прочитанное"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    logger.info(f'Сообщение #{message_id} отмечено как прочитанное')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Сообщение отмечено как прочитанное', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/admin/message/<int:message_id>/unread', methods=['POST'])
@login_required
def mark_message_unread(message_id):
    """Отметить сообщение как непрочитанное"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = False
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Сообщение отмечено как непрочитанное', 'info')
    return redirect(url_for('admin_messages'))


@app.route('/admin/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Удалить сообщение"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    logger.info(f'Сообщение #{message_id} удалено')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Сообщение удалено', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/admin/cases')
@login_required
def admin_cases():
    """Управление кейсами"""
    cases = Case.query.order_by(Case.created_at.desc()).all()
    return render_template('admin/cases.html', cases=cases)


# ==================== ИНИЦИАЛИЗАЦИЯ БД ====================

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        # Создание директорий
        db_dir = os.path.join(basedir, 'database')
        images_dir = os.path.join(basedir, 'static', 'images')
        os.makedirs(db_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        # Создание таблиц БД
        db.create_all()
        
        # Создание администратора и кейсов
        create_admin()
        create_default_cases()
        
        logger.info('База данных инициализирована')


# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    # Инициализация БД перед запуском
    init_db()
    
    # Запуск сервера разработки
    app.run(debug=True, host='0.0.0.0', port=5000)
