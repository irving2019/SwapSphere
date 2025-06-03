from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Показать список всех зарегистрированных пользователей'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('date_joined')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('В базе данных нет зарегистрированных пользователей'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Всего пользователей: {users.count()}'))
        self.stdout.write('')
        
        for user in users:
            status = '✅ Активен' if user.is_active else '❌ Неактивен'
            admin_status = '👑 Админ' if user.is_superuser else '👤 Пользователь'
            
            self.stdout.write(f'ID: {user.id:3d} | Username: {user.username:20s} | Email: {user.email:30s}')
            self.stdout.write(f'     | Статус: {status:12s} | Роль: {admin_status:15s}')
            self.stdout.write(f'     | Дата регистрации: {user.date_joined.strftime("%d.%m.%Y %H:%M")}')
            self.stdout.write(f'     | Последний вход: {user.last_login.strftime("%d.%m.%Y %H:%M") if user.last_login else "Никогда"}')
            self.stdout.write('-' * 80)
