# 🔄 SwapSphere - Платформа для обмена вещами

Современная веб-платформа для обмена товарами с функционалом социальной сети на Django.

## ✨ Основные возможности

- 📝 **Управление объявлениями** - создание, редактирование с множественными изображениями и категориями
- 🔄 **Система обмена** - предложения со статусами (Ожидание/Принято/Отклонено/Отменено/Завершено)
- 💬 **Комментарии и общение** - комментарии к объявлениям с возможностью ответов
- 📧 **Личные сообщения** - приватные беседы между пользователями с уведомлениями
- 👤 **Профили пользователей** - настройка профиля, загрузка аватара, просмотр истории обменов
- 🚫 **Блокировка пользователей** - система модерации контента
- 🔍 **Расширенный поиск** - по категориям, статусу, состоянию и параметрам
- 📱 **Адаптивный дизайн** - современный UI с анимациями для всех устройств
- 🔒 **Безопасность пользователей** - валидация паролей и защита данных

## 🛠️ Технологии

- **Backend**: Django 4.2.21 + Django REST Framework 3.16.0
- **Frontend**: Bootstrap 5 + JavaScript
- **База данных**: SQLite (разработка), PostgreSQL 15 (продакшн)
- **Развертывание**: Docker + Nginx + Gunicorn
- **Кеширование**: Redis

## 🚀 Быстрый старт

### 🐳 Docker (рекомендуется)
```bash
git clone https://github.com/your-username/SwapSphere.git
cd SwapSphere
docker-compose -f docker-compose.dev.yml up --build   # для разработки
# или
docker-compose up --build                            # для продакшена
docker-compose exec web python manage.py createsuperuser
```

### 💻 Локальная разработка
```bash
# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установка зависимостей и настройка
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```

🌐 **Приложение**: http://127.0.0.1:8000 | **Админ-панель**: http://127.0.0.1:8000/admin/

## 📁 Структура проекта

- **ads/** - основное приложение (модели, представления, формы)
  - **models.py** - модели данных (Ad, ExchangeProposal, UserProfile, ...)
  - **views.py** - представления для обработки запросов
  - **forms.py** - формы для работы с данными
  - **templates/** - HTML шаблоны интерфейса
  - **templatetags/** - пользовательские теги шаблонов
- **static/** - статические ресурсы (CSS, JS, изображения)
- **media/** - загружаемые пользователем файлы
- **swapsphere/** - основной модуль проекта с настройками
- **docker-compose.yml** - настройки контейнеризации с health checks

## 🧪 Тестирование

```bash
# Запуск тестов Django
python manage.py test

# Запуск полного автоматического тестирования
python test_full_autotest.py

# Запуск с отчетом о покрытии
coverage run manage.py test
coverage report
```

## ⚙️ Настройки проекта

Создайте файл `.env` в корне проекта:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
POSTGRES_USER=swapsphere
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=swapsphere
SENTRY_DSN=your-sentry-dsn
```

## 🔄 Система обмена

| Статус      | Цвет | Описание                   |
|-------------|------|----------------------------|
| **Pending** | 🟡    | Ожидает ответа получателя  |
| **Accepted**| 🟢    | Предложение принято        |
| **Rejected**| 🔴    | Предложение отклонено      |
| **Cancelled**| ⚫    | Предложение отменено       |
| **Completed**| 🔵    | Обмен завершен и в архиве  |

## 📝 Функции профиля

- Загрузка и редактирование аватара с предпросмотром
- Управление личной информацией и настройками приватности
- Просмотр истории объявлений и обменов
- Управление уведомлениями о новых сообщениях и предложениях
- Архивирование завершенных обменов

## 🛡️ Приватность и безопасность

- Пользователи могут скрыть: Email, полное имя, дату рождения, номер телефона
- Строгие требования к паролям: 8-16 символов, буквы разного регистра, цифры, спецсимволы
- Поддержка автозаполнения логина и пароля в браузере
- Защита от XSS и CSRF-атак

## 📱 Адаптивность

Платформа полностью адаптирована для работы на мобильных устройствах:
- Отзывчивый интерфейс на основе Bootstrap 5
- Оптимизированные изображения с ограничением размера (500x500px)

## 🤝 Разработка и вклад в проект

```bash
# Создание новой ветки для функциональности
git checkout -b feature/имя-функции

# После внесения изменений
python manage.py test  # Запуск тестов
```

**Стандарты кода**: PEP 8, документация с docstrings, обязательное покрытие тестами


**SwapSphere** - делаем обмен вещами простым и удобным! 🌍✨