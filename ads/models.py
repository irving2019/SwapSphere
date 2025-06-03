import os
from django.db import models
from django.contrib.auth.models import User

class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/У'),
    ]

    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('in_exchange', 'В обмене'),
        ('exchanged', 'Обменен'),
    ]

    CATEGORY_CHOICES = [
        # Техника и электроника
        ('smartphones', 'Смартфоны и телефоны'),
        ('computers', 'Компьютеры и ноутбуки'),
        ('tablets', 'Планшеты'),
        ('audio_video', 'Аудио и видео'),
        ('cameras', 'Фото и видеокамеры'),
        ('gaming', 'Игровые консоли'),
        ('appliances', 'Бытовая техника'),
        
        # Одежда и обувь
        ('mens_clothing', 'Мужская одежда'),
        ('womens_clothing', 'Женская одежда'),
        ('kids_clothing', 'Детская одежда'),
        ('shoes', 'Обувь'),
        ('accessories', 'Аксессуары'),
        
        # Дом и сад
        ('furniture', 'Мебель'),
        ('home_decor', 'Декор и интерьер'),
        ('kitchen', 'Кухонные принадлежности'),
        ('garden', 'Сад и огород'),
        ('repair', 'Ремонт и строительство'),
        
        # Хобби и досуг
        ('books', 'Книги и журналы'),
        ('music_instruments', 'Музыкальные инструменты'),
        ('art_crafts', 'Творчество и рукоделие'),
        ('collectibles', 'Коллекционирование'),
        
        # Спорт и отдых
        ('sports_equipment', 'Спортивные товары'),
        ('outdoor', 'Туризм и отдых'),
        ('bicycles', 'Велосипеды'),
        ('fitness', 'Фитнес'),
        
        # Транспорт
        ('auto_parts', 'Автозапчасти'),
        ('motorcycles', 'Мотоциклы'),
        ('auto_accessories', 'Автоаксессуары'),
        
        # Детские товары
        ('toys', 'Игрушки'),
        ('baby_products', 'Товары для малышей'),
        ('kids_transport', 'Детский транспорт'),
        
        # Красота и здоровье
        ('cosmetics', 'Косметика и парфюмерия'),
        ('health', 'Здоровье и медицина'),
        
        # Животные
        ('pet_supplies', 'Товары для животных'),
        
        # Недвижимость и услуги
        ('real_estate', 'Недвижимость'),
        ('services', 'Услуги'),
        
        # Другое
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')
    image_file = models.ImageField(upload_to='ads/', blank=True, null=True, verbose_name='Изображение')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other', verbose_name='Категория')
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='used', verbose_name='Состояние')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_image_url(self):
        """Возвращает URL изображения (приоритет у загруженного файла)"""
        if self.image_file:
            return self.image_file.url
        elif self.image_url:
            return self.image_url
        return None
    
    def get_main_image_url(self):
        """Возвращает URL главного изображения"""
        # Сначала проверяем новые изображения
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image.get_image_url()
        
        # Если нет главного, берем первое изображение
        first_image = self.images.first()
        if first_image:
            return first_image.get_image_url()
        
        # Если нет новых изображений, используем старые поля
        return self.get_image_url()
    
    def get_all_images(self):
        """Возвращает все изображения объявления"""
        images = []
        
        # Добавляем изображения из новой модели
        for img in self.images.all():
            images.append({
                'url': img.get_image_url(),
                'is_main': img.is_main,
                'order': img.order,
                'id': img.id
            })
        
        # Если нет изображений в новой модели, добавляем из старых полей
        if not images:
            url = self.get_image_url()
            if url:
                images.append({
                    'url': url,
                    'is_main': True,
                    'order': 0,
                    'id': None
                })
        
        return images
    
    @property
    def image(self):
        """Свойство для совместимости с существующим кодом"""
        return self.get_main_image_url()

class AdImage(models.Model):
    """Модель для хранения множественных изображений объявления"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images', verbose_name='Объявление')
    image_file = models.ImageField(upload_to='ads/images/', blank=True, null=True, verbose_name='Изображение')
    image_url = models.URLField(blank=True, null=True, verbose_name='URL изображения')
    is_main = models.BooleanField(default=False, verbose_name='Главное изображение')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Изображение объявления'
        verbose_name_plural = 'Изображения объявления'
        ordering = ['order', 'created_at']
        unique_together = [['ad', 'order']]

    def __str__(self):
        return f'Изображение {self.order + 1} для {self.ad.title}'

    def get_image_url(self):
        """Возвращает URL изображения (приоритет у загруженного файла)"""
        if self.image_file:
            return self.image_file.url
        elif self.image_url:
            return self.image_url
        return None

    def save(self, *args, **kwargs):
        # Проверяем, что у объявления не более 5 изображений
        if not self.pk:  # Новое изображение
            existing_count = AdImage.objects.filter(ad=self.ad).count()
            if existing_count >= 5:
                raise ValueError('У объявления не может быть более 5 изображений')
            
            # Устанавливаем порядок
            if self.order == 0:
                max_order = AdImage.objects.filter(ad=self.ad).aggregate(
                    models.Max('order'))['order__max']
                self.order = (max_order or -1) + 1
        
        # Если это главное изображение, убираем флаг у других
        if self.is_main:
            AdImage.objects.filter(ad=self.ad).exclude(pk=self.pk).update(is_main=False)
        
        super().save(*args, **kwargs)


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals',
                                 verbose_name='Отправитель')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals',
                                  verbose_name='Получатель')
    message = models.TextField(verbose_name='Сообщение', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending',
                            verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Поля для отслеживания прочитанности
    is_read_by_sender = models.BooleanField(default=True, verbose_name='Прочитано отправителем')
    is_read_by_receiver = models.BooleanField(default=False, verbose_name='Прочитано получателем')

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']

    def __str__(self):
        return f'Обмен {self.ad_sender} на {self.ad_receiver}'
    def can_be_cancelled(self):
        """Может ли предложение быть отменено"""
        return self.status == 'pending'
    
    def get_status_display_class(self):
        """Возвращает CSS класс для статуса"""
        status_classes = {
            'pending': 'bg-warning text-dark',
            'accepted': 'bg-success',
            'rejected': 'bg-danger',
            'cancelled': 'bg-secondary',
            'completed': 'bg-info',
        }
        return status_classes.get(self.status, 'bg-secondary')

class UserProfile(models.Model):
    AVATAR_CHOICES = [
        ('default1.png', 'Аватар 1'),
        ('default2.png', 'Аватар 2'),
        ('default3.png', 'Аватар 3'),
        ('default4.png', 'Аватар 4'),
        ('default5.png', 'Аватар 5'),
        ('default6.png', 'Аватар 6'),
        ('default7.png', 'Аватар 7'),
        ('default8.png', 'Аватар 8'),
        ('default9.png', 'Аватар 9'),
        ('default10.png', 'Аватар 10'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Пользовательский аватар'
    )
    default_avatar = models.CharField(
        max_length=20,
        choices=AVATAR_CHOICES,
        default='default1.png',
        verbose_name='Аватар по умолчанию'
    )
    
    # Расширенные поля профиля
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Город'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Верифицированный пользователь'
    )
    show_phone = models.BooleanField(
        default=True,
        verbose_name='Показывать номер телефона'
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name='Показывать email'
    )
    show_full_name = models.BooleanField(
        default=True,
        verbose_name='Показывать полное имя'
    )
    show_birth_date = models.BooleanField(
        default=False,
        verbose_name='Показывать дату рождения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания профиля',
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления профиля',
        null=True
    )

    def get_avatar_url(self):
        if self.avatar:
            try:
                if os.path.exists(self.avatar.path):
                    return self.avatar.url
            except:
                pass
        return f'/static/images/avatars/default/{self.default_avatar}'
    
    def get_full_name(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    def get_age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def __str__(self):
        return f'Профиль {self.user.username}'

class AdComment(models.Model):
    """Модель комментариев к объявлениям"""
    ad = models.ForeignKey(
        Ad, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Объявление'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    content = models.TextField(
        max_length=1000,
        verbose_name='Текст комментария'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Родительский комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитан автором объявления'
    )

    class Meta:
        verbose_name = 'Комментарий к объявлению'
        verbose_name_plural = 'Комментарии к объявлениям'
        ordering = ['created_at']

    def __str__(self):
        if self.parent:
            return f'Ответ {self.author.username} на комментарий к "{self.ad.title}"'
        return f'Комментарий {self.author.username} к "{self.ad.title}"'

    def get_replies(self):
        """Получить все ответы на этот комментарий"""
        return self.replies.all().order_by('created_at')

    def is_reply(self):
        """Проверить, является ли это ответом на другой комментарий"""
        return self.parent is not None

    def can_reply(self, user):
        """Проверить, может ли пользователь отвечать на этот комментарий"""
        # Автор объявления может отвечать на любые комментарии
        if user == self.ad.user:
            return True
        # Автор комментария может отвечать на ответы к своему комментарию
        return user == self.author

    def __str__(self):
        return f'Комментарий {self.author.username} к {self.ad.title}'


class UserBlock(models.Model):
    """Модель для блокировки пользователей"""
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocking',
        verbose_name='Блокирующий пользователь'
    )
    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by',
        verbose_name='Заблокированный пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата блокировки'
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Причина блокировки'
    )

    class Meta:
        unique_together = ('blocker', 'blocked')
        verbose_name = 'Блокировка пользователя'
        verbose_name_plural = 'Блокировки пользователей'

    def __str__(self):
        return f'{self.blocker.username} заблокировал {self.blocked.username}'


class PrivateMessage(models.Model):
    """Модель для личных сообщений"""
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Тема сообщения'
    )
    content = models.TextField(
        verbose_name='Содержание сообщения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отправки'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Родительское сообщение'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Личное сообщение'
        verbose_name_plural = 'Личные сообщения'

    def is_blocked(self):
        """Проверить, заблокирован ли один из пользователей"""
        return UserBlock.objects.filter(
            models.Q(blocker=self.sender, blocked=self.receiver) |
            models.Q(blocker=self.receiver, blocked=self.sender)
        ).exists()

    def get_conversation_id(self):
        """Получить ID беседы между двумя пользователями"""
        user_ids = sorted([self.sender.id, self.receiver.id])
        return f"{user_ids[0]}_{user_ids[1]}"

    def __str__(self):
        return f'Сообщение от {self.sender.username} к {self.receiver.username}: {self.subject}'


class Conversation(models.Model):
    """Модель для группировки сообщений в беседы"""
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        verbose_name='Участники'
    )
    last_message = models.ForeignKey(
        PrivateMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversation_last',
        verbose_name='Последнее сообщение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Беседа'
        verbose_name_plural = 'Беседы'

    def get_other_participant(self, user):
        """Получить собеседника"""
        return self.participants.exclude(id=user.id).first()

    def get_unread_count(self, user):
        """Получить количество непрочитанных сообщений для пользователя"""
        return PrivateMessage.objects.filter(
            receiver=user,
            sender__in=self.participants.exclude(id=user.id),
            is_read=False
        ).count()

    def __str__(self):
        participants = ', '.join([user.username for user in self.participants.all()])
        return f'Беседа: {participants}'