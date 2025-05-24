# SwapSphere - Платформа для обмена вещами

SwapSphere - это веб-приложение на Django для организации обмена вещами между пользователями. Пользователи могут размещать объявления о товарах для обмена, просматривать чужие объявления и отправлять предложения на обмен.

## Требования

- Python 3.8+
- Docker и Docker Compose (опционально)
- PostgreSQL (при использовании Docker) или SQLite (локальная разработка)

## Установка и запуск

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/irving2019/SwapSphere
cd SwapSphere
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
.\venv\Scripts\Activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер разработки:
```bash
python manage.py runserver
```

### Запуск через Docker

1. Соберите и запустите контейнеры:
```bash
docker-compose up --build
```

2. В отдельном терминале создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

## API Endpoints

### Объявления
- `GET /api/ads/` - список всех объявлений
- `POST /api/ads/` - создание объявления
- `GET /api/ads/{id}/` - детали объявления
- `PUT /api/ads/{id}/` - обновление объявления
- `DELETE /api/ads/{id}/` - удаление объявления

### Предложения обмена
- `GET /api/proposals/` - список предложений обмена
- `POST /api/proposals/` - создание предложения обмена
- `POST /api/proposals/{id}/accept/` - принять предложение
- `POST /api/proposals/{id}/reject/` - отклонить предложение

## Тестирование

Для запуска тестов используйте команду:
```bash
python manage.py test
```

## Особенности

- Полнотекстовый поиск по объявлениям
- Фильтрация по категории и состоянию товара
- Система обмена предложениями с подтверждением
- REST API с поддержкой пагинации
- Админ-панель Django для управления данными

## Документация API

Документация API доступна по адресу `/api/` при запущенном сервере. Она предоставляет интерактивный интерфейс для тестирования API endpoints.