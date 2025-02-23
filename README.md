# 🎓 LMS Project

Система управления обучением (Learning Management System), разрабо��анная на Django.

## 🛠 Технологии

- Python
- Django
- Django REST Framework
- PostgreSQL
- HTML

## 📋 Функциональности

- Административная панель Django
- REST API для управления учебными материалами
- Пользовательская модель аутентификации
- Система управления медиафайлами

## 🚀 Установка и запуск

1. Клонируйте репозиторий:

2. git clone https://github.com/gvriil/LMS_Project_5.git
```bash
cd LMS_Project_5
```
3. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
```
source venv/bin/activate  # для Linux/macOS

4. Установите зависимости:
```
pip install -r requirements.txt
```
5. Настройте базу данных PostgreSQL:
Создайте базу данных:
```
CREATE DATABASE lms_db;
```
Параметры подключения к БД:
```
NAME: lms_db
USER: postgres
PASSWORD: 12345
HOST: 127.0.0.1
PORT: 5432
Выполните миграции:
```
6. Выполните миграции:
```
python manage.py migrate
```
7. Запустите сервер разработки:
```
python manage.py runserver
```
🔍 API Endpoints
/ - Главная страница
/admin/ - Административная панель Django
/api/ - API endpoints для работы с учебными материалами
/media/ - Доступ к медиафайлам

📁 Структура проекта
config/ - Основные настройки проекта
users/ - Приложение для работы с пользователями
materials/ - Приложение для работы с учебными материалами
templates/ - HTML шаблоны
media/ - Директория для медиафайлов

🔒 Переменные окружения
Для production необходимо настроить:  
SECRET_KEY
DEBUG=False
ALLOWED_HOSTS
DATABASE_URL

👥 Автор
https://github.com/gvriil

📝 Лицензия
MIT License
```bash
pip install -r requirements.txt
```