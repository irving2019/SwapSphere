# 🔄 SwapSphere - Платформа для обмена вещами

Современная веб-платформа для обмена товарами с функционалом социальной сети на Django.

## ✨ Основные возможности

- 📝 **Объявления** - создание с множественными изображениями и категориями
- 🔄 **Система обмена** - предложения со статусами (Ожидание/Принято/Отклонено/Отменено)  
- 💬 **Комментарии** - к объявлениям с возможностью ответов
- 📧 **Личные сообщения** - приватные беседы между пользователями
- 👤 **Профили** - с настройками приватности и аватарами
- 🚫 **Блокировка пользователей** - система модерации
- 🔍 **Поиск и фильтрация** - по категориям и параметрам
- 📱 **Адаптивный дизайн** - современный UI с анимациями

## 🛠️ Технологии

**Backend**: Django 4.2 + DRF | **Frontend**: Bootstrap 5 + JS | **DB**: SQLite/PostgreSQL | **Deploy**: Docker

## 🚀 Быстрый старт

### 🐳 Docker (рекомендуется)
```bash
git clone https://github.com/your-username/SwapSphere.git
cd SwapSphere
docker-compose up --build
docker-compose exec web python manage.py createsuperuser
```

### 💻 Локально
```bash
python -m venv venv
venv\Scripts\activate  # Windows | source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

🌐 **Приложение**: http://127.0.0.1:8000 | **Админ**: /admin

## 📁 Основные компоненты

- **ads/** - модели (User, Ad, Exchange, Message), представления, формы
- **templates/** - HTML-шаблоны с адаптивным дизайном
- **static/** - CSS, JS, изображения
- **test_full_autotest.py** - комплексные тесты системы
- **docker-compose.yml** - контейнеризация с health checks

## 🧪 Тестирование

```bash
python test_full_autotest.py  # Полный автотест
python manage.py test         # Django тесты
```

## ⚙️ Настройки

Создайте `.env` файл (см. `.env.example`):
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🔄 Система обмена

| Статус | Цвет | Описание |
|--------|------|----------|
| **Pending** | 🟡 | Ожидает ответа |
| **Accepted** | 🟢 | Принято |
| **Rejected** | 🔴 | Отклонено |
| **Cancelled** | ⚫ | Отменено |

## 🛡️ Приватность

Пользователи могут скрыть: Email, полное имя, дату рождения, номер телефона

## 🤝 Разработка

```bash
git checkout -b feature/new-feature
python test_full_autotest.py  # тестирование
```

**Стандарты**: PEP 8, docstrings, тесты для новых функций


**SwapSphere** - делаем обмен вещами простым и удобным! 🌍✨