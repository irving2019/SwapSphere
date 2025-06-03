#!/usr/bin/env python
"""
🧪 ПОЛНЫЙ АВТОТЕСТ SWAPSPHERE

Комплексный тест всех функций платформы для обмена товарами
Включает в себя все ранее созданные тесты в одном месте
"""

import os
import sys

# Настройка Django ПЕРЕД любыми импортами
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swapsphere.settings')

import django
django.setup()

# Теперь можно импортировать Django модели
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import io

from ads.models import UserProfile, Ad, AdImage, ExchangeProposal


class SwapSphereFullTest:
    """Полный тест функциональности SwapSphere"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        
    def print_header(self, title):
        """Печать заголовка теста"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
        
    def print_test(self, test_name, status, details=""):
        """Печать результата теста"""
        self.total_tests += 1
        if status:
            self.passed_tests += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   ⚠️  {details}")
    
    def test_database_setup(self):
        """Тест настройки базы данных"""
        self.print_header("ТЕСТ БАЗЫ ДАННЫХ")
        
        try:
            # Проверка подключения к БД
            users_count = User.objects.count()
            self.print_test("Подключение к базе данных", True, f"Пользователей: {users_count}")
            
            # Проверка моделей
            categories_count = len(Ad.CATEGORY_CHOICES)
            self.print_test("Категории товаров", True, f"Категорий: {categories_count}")
            
            ads_count = Ad.objects.count()
            self.print_test("Модель Ad", True, f"Объявлений: {ads_count}")
            
            profiles_count = UserProfile.objects.count()
            self.print_test("Модель UserProfile", True, f"Профилей: {profiles_count}")
            
            return True
            
        except Exception as e:
            self.print_test("Настройка базы данных", False, str(e))
            return False
    
    def test_user_system(self):
        """Тест системы пользователей"""
        self.print_header("ТЕСТ СИСТЕМЫ ПОЛЬЗОВАТЕЛЕЙ")
        
        try:
            # Создание тестового пользователя
            test_user = User.objects.filter(username='test_user').first()
            if not test_user:
                test_user = User.objects.create_user(
                    username='test_user',
                    email='test@example.com',
                    password='testpass123'
                )
            
            self.print_test("Создание пользователя", True, f"ID: {test_user.id}")
              # Создание профиля
            profile, created = UserProfile.objects.get_or_create(
                user=test_user,
                defaults={'phone_number': '+7123456789'}
            )
            
            self.print_test("Создание профиля", True, f"ID: {profile.id}")
            
            return test_user
            
        except Exception as e:
            self.print_test("Система пользователей", False, str(e))
            return None
    
    def test_categories(self):
        """Тест системы категорий"""
        self.print_header("ТЕСТ СИСТЕМЫ КАТЕГОРИЙ")
        
        try:
            # Проверка предустановленных категорий
            categories = Ad.CATEGORY_CHOICES
            self.print_test("Загрузка категорий", True, f"Доступно: {len(categories)}")
            
            # Проверка некоторых конкретных категорий
            category_keys = [choice[0] for choice in categories]
            
            expected_categories = ['smartphones', 'computers', 'books', 'clothing']
            for cat in expected_categories:
                if any(cat in key for key in category_keys):
                    self.print_test(f"Категория '{cat}'", True)
                else:
                    self.print_test(f"Категория '{cat}'", False, "Не найдена")
            
            return True
            
        except Exception as e:
            self.print_test("Система категорий", False, str(e))
            return False
    
    def test_ads_system(self, test_user):
        """Тест системы объявлений"""
        self.print_header("ТЕСТ СИСТЕМЫ ОБЪЯВЛЕНИЙ")
        
        if not test_user:
            self.print_test("Система объявлений", False, "Нет тестового пользователя")
            return None
        
        try:
            # Создание объявления
            test_ad = Ad.objects.filter(user=test_user).first()
            if not test_ad:
                test_ad = Ad.objects.create(
                    user=test_user,
                    title='Тестовое объявление',
                    description='Описание тестового объявления',
                    category='smartphones',  # Используем значение из CATEGORY_CHOICES
                    condition='new'
                )
            
            self.print_test("Создание объявления", True, f"ID: {test_ad.id}")
            
            # Создание изображения для объявления
            if PIL_AVAILABLE:
                # Создаем тестовое изображение
                image = Image.new('RGB', (100, 100), color='red')
                image_io = io.BytesIO()
                image.save(image_io, format='JPEG')
                image_io.seek(0)
                
                test_image = SimpleUploadedFile(
                    name='test.jpg',
                    content=image_io.getvalue(),
                    content_type='image/jpeg'
                )                # Определяем следующий порядковый номер для изображения
                next_order = AdImage.objects.filter(ad=test_ad).count()
                
                ad_image = AdImage.objects.create(
                    ad=test_ad,
                    image_file=test_image,
                    order=next_order
                )
                
                self.print_test("Добавление изображения", True, f"ID: {ad_image.id}")
            else:
                self.print_test("Добавление изображения", False, "PIL не установлен")
            
            return test_ad
            
        except Exception as e:
            self.print_test("Система объявлений", False, str(e))
            return None
    
    def test_exchange_system(self, test_ad):
        """Тест системы обмена"""
        self.print_header("ТЕСТ СИСТЕМЫ ОБМЕНА")
        
        if not test_ad:
            self.print_test("Система обмена", False, "Нет тестового объявления")
            return False
        
        try:
            # Создание второго пользователя для обмена
            user2 = User.objects.filter(username='test_user2').first()
            if not user2:
                user2 = User.objects.create_user(
                    username='test_user2',
                    email='test2@example.com',
                    password='testpass123'
                )
            
            ad2 = Ad.objects.filter(user=user2).first()
            if not ad2:
                ad2 = Ad.objects.create(
                    user=user2,
                    title='Второе тестовое объявление',
                    description='Описание второго объявления',
                    category='computers',  # Используем значение из CATEGORY_CHOICES
                    condition='used'
                )
            
            self.print_test("Создание второго пользователя и объявления", True)
              # Создание предложения обмена
            proposal = ExchangeProposal.objects.create(
                ad_sender=test_ad,
                ad_receiver=ad2,
                message='Предлагаю обмен',
                status='pending'
            )
            self.print_test("Создание предложения обмена", True, f"ID: {proposal.id}")
            
            # Изменение статуса
            proposal.status = 'accepted'
            proposal.save()
            self.print_test("Принятие предложения", True)
            
            return True
            
        except Exception as e:
            self.print_test("Система обмена", False, str(e))
            return False
    
    def test_search_and_filter(self):
        """Тест поиска и фильтрации"""
        self.print_header("ТЕСТ ПОИСКА И ФИЛЬТРАЦИИ")
        
        try:
            # Поиск по категории
            smartphone_ads = Ad.objects.filter(category='smartphones')
            self.print_test("Поиск по категории", True, f"Найдено: {smartphone_ads.count()}")
            
            # Поиск по состоянию
            new_ads = Ad.objects.filter(condition='new')
            self.print_test("Фильтр по состоянию", True, f"Новых товаров: {new_ads.count()}")
            
            # Поиск по тексту в заголовке
            text_search = Ad.objects.filter(title__icontains='тест')
            self.print_test("Текстовый поиск", True, f"Найдено: {text_search.count()}")
            
            return True
            
        except Exception as e:
            self.print_test("Поиск и фильтрация", False, str(e))
            return False
    
    def test_user_profile_features(self):
        """Тест функций профиля пользователя"""
        self.print_header("ТЕСТ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ")
        
        try:
            # Получение профиля
            test_user = User.objects.filter(username='test_user').first()
            if not test_user:
                self.print_test("Получение профиля", False, "Тестовый пользователь не найден")
                return False
            
            profile = UserProfile.objects.get_or_create(user=test_user)[0]
            
            # Обновление профиля
            profile.location = 'Москва'
            profile.bio = 'Тестовая биография'
            profile.save()
            
            self.print_test("Обновление профиля", True)
            
            # Получение объявлений пользователя
            user_ads = Ad.objects.filter(user=test_user)
            self.print_test("Объявления пользователя", True, f"Количество: {user_ads.count()}")
            
            return True
            
        except Exception as e:
            self.print_test("Профиль пользователя", False, str(e))
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК ПОЛНОГО АВТОТЕСТА SWAPSPHERE")
        print("=" * 60)
        
        # 1. Тест базы данных
        db_ok = self.test_database_setup()
        
        # 2. Тест пользователей
        test_user = self.test_user_system()
        
        # 3. Тест категорий
        categories_ok = self.test_categories()
        
        # 4. Тест объявлений
        test_ad = self.test_ads_system(test_user)
        
        # 5. Тест обмена
        exchange_ok = self.test_exchange_system(test_ad)
        
        # 6. Тест поиска
        search_ok = self.test_search_and_filter()
        
        # 7. Тест профиля
        profile_ok = self.test_user_profile_features()
        
        # Итоги
        self.print_results()
    
    def print_results(self):
        """Печать итоговых результатов"""
        print("\n" + "=" * 60)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print(f"✅ Пройдено тестов: {self.passed_tests}")
        print(f"❌ Провалено тестов: {self.failed_tests}")
        print(f"📈 Всего тестов: {self.total_tests}")
        
        if self.failed_tests == 0:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("SwapSphere готов к использованию! 🚀")
        else:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"\n⚠️  Успешность: {success_rate:.1f}%")
            if success_rate >= 80:
                print("Система в основном работает корректно ✅")
            elif success_rate >= 60:
                print("Система работает с некоторыми проблемами ⚠️")
            else:
                print("Система требует серьезной доработки ❌")


def main():
    """Главная функция запуска тестов"""
    print("🔧 Инициализация тестов...")
    
    try:
        # Создание экземпляра тестера
        tester = SwapSphereFullTest()
        
        # Запуск всех тестов
        tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске тестов: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
