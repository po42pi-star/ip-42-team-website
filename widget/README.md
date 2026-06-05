# FAQ Widget

AI-чат-бот на базе RAG (Retrieval-Augmented Generation) для ответов на вопросы о компании IP-42-Team.

## 📁 Структура

```
widget/
├── app.py              # FastAPI сервер (порт 8000)
├── build_index.py      # Построение векторного индекса
├── rag_index.py        # RAG модуль
├── .env                # API ключи
├── data/
│   ├── faqs.json       # FAQ база (24 вопроса)
│   ├── doc1-5.txt      # Дополнительные документы
│   ├── faiss_index.bin # Векторный индекс
│   └── faqs_metadata.npy
└── start-faq.ps1       # Скрипт запуска
```

## ⚙️ Установка

### 1. Зависимости

```powershell
pip install fastapi uvicorn openai httpx faiss-cpu python-dotenv
```

### 2. Настройка .env

Создайте `widget/.env`:

```
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

⚠️ **Важно:** используется `OPENAI_BASE_URL` (не `OPENAI_API_BASE_URL`)

## 🚀 Запуск

### ⚠️ Критично: только через uvicorn!

```powershell
# НЕ работает:
python app.py

# Работает:
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Пошагово

```powershell
cd widget

# 1. Построить индекс (первый запуск)
python build_index.py

# 2. Запустить сервер
uvicorn app:app --host 0.0.0.0 --port 8000
```

Сервер запустится на **http://localhost:8000**

### Проверка

- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/health` — Health check

### Через скрипт

```powershell
.\start-faq.ps1
```

## 🤖 API Endpoints

### `POST /chat`

Отправить сообщение и получить ответ:

```json
{
  "message": "Ваш вопрос",
  "top_k": 3
}
```

### `GET /health`

Проверка работоспособности:

```json
{"status": "ok"}
```

## 📝 Добавление FAQ

### Через JSON

1. Откройте `data/faqs.json`
2. Добавьте вопрос:

```json
{
  "question": "Как с вами связаться?",
  "answer": "Email: po42pi@gmail.com, Телефон: +7 (909) 323-66-00"
}
```

3. Перестройте индекс:

```powershell
python build_index.py
```

### Через текстовые файлы

Добавьте `*.txt` в `data/`, затем:

```powershell
python build_index.py
```

## 🔧 Troubleshooting

### Сервер сразу закрывается

**Проблема:** `python app.py` не запускает сервер

**Решение:**
```powershell
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Ошибка "OPENAI_API_KEY is not set"

**Проверьте:**
1. Файл `.env` существует в `widget/`
2. Содержит правильный ключ:
```
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
```

### Не удалось получить ответ

**Проверьте:**
1. ✅ FAQ сервер запущен на порту 8000
2. ✅ API ключ корректен
3. ✅ Векторный индекс существует (`faiss_index.bin`)

### Индекс не найден

```powershell
python build_index.py
```

## 💻 Технологии

- **Backend:** FastAPI, Python 3.9+
- **AI:** ProxyAPI (OpenAI-совместимый)
- **Vector Search:** FAISS
- **Embeddings:** text-embedding-3-small

## 🔗 Интеграция с сайтом

Виджет подключён в `templates/base.html`:

```html
<script src="{{ url_for('static', filename='widget/chat-widget.js') }}"></script>
```

**Конфигурация в `config.py`:**
```python
FAQ_API_BASE = 'http://localhost:8000'
```

**Для production (через nginx):**
```python
FAQ_API_BASE = 'http://193.233.174.246/faq-api'
```

## 📄 FAQ база

24 вопроса по профилю компании:
- О компании и технологиях
- Telegram-боты и AI-ассистенты
- Кейсы и проекты
- Стоимость и сроки
- Процесс разработки
- Контакты

---

**Проект IP-42-Team**
