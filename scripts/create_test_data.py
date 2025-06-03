#!/usr/bin/env python
import os
import django
import sys

# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swapsphere.settings')
django.setup()

from django.contrib.auth.models import User
from ads.models import Ad

# Создаем тестового пользователя, если его нет
test_user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Тест',
        'last_name': 'Пользователь'
    }
)

if created:
    test_user.set_password('testpassword')
    test_user.save()
    print(f"Создан пользователь: {test_user.username}")

# Создаем тестовые объявления
test_ads = [
    {
        'title': 'iPhone 13 Pro',
        'description': 'Продаю iPhone 13 Pro в отличном состоянии. Все функции работают идеально.',
        'category': 'electronics',
        'condition': 'used',
        'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400'
    },
    {
        'title': 'Куртка зимняя Nike',
        'description': 'Теплая зимняя куртка Nike, размер M. Носилась один сезон.',
        'category': 'clothing',
        'condition': 'used',
        'image_url': 'https://images.unsplash.com/photo-1544966503-7cc5ac882d5d?w=400'
    },
    {
        'title': 'Учебник по Python',
        'description': 'Книга "Изучаем Python" от O\'Reilly. В хорошем состоянии.',
        'category': 'books',
        'condition': 'used',
        'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'
    },
    {
        'title': 'Футбольный мяч Adidas',
        'description': 'Профессиональный футбольный мяч Adidas. Новый, в упаковке.',
        'category': 'sports',
        'condition': 'new',
        'image_url': 'https://images.unsplash.com/photo-1556992220-b6c0a4b9cf71?w=400'
    },
    {
        'title': 'PlayStation 5',
        'description': 'Игровая консоль PlayStation 5 с двумя джойстиками и несколькими играми.',
        'category': 'games',
        'condition': 'used',
        'image_url': 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400'
    }
]

for ad_data in test_ads:
    ad, created = Ad.objects.get_or_create(
        title=ad_data['title'],
        user=test_user,
        defaults=ad_data
    )
    if created:
        print(f"Создано объявление: {ad.title}")
    else:
        print(f"Объявление уже существует: {ad.title}")

print(f"\nВсего объявлений в базе: {Ad.objects.count()}")
print("Тестовые данные успешно созданы!")
