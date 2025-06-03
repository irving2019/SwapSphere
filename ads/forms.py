from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Ad, UserProfile, ExchangeProposal, AdComment, PrivateMessage, UserBlock, AdImage


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(
        max_length=20, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 999-99-99'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
        
        # Изменяем текст подсказки для полей пароля
        self.fields['password1'].help_text = 'Пароль должен содержать 8-16 символов, может включать буквы разного регистра, цифры и специальные символы'
        
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Проверка длины пароля (от 8 до 16 символов)
        if len(password1) < 8 or len(password1) > 16:
            raise ValidationError('Пароль должен содержать от 8 до 16 символов.')
            
        # Проверка наличия букв в разном регистре
        if not (any(c.islower() for c in password1) and any(c.isupper() for c in password1)):
            raise ValidationError('Пароль должен содержать буквы в верхнем и нижнем регистре.')
              # Проверка наличия цифр
        if not any(c.isdigit() for c in password1):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру.')
          
        return password1


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }


class AdImageForm(forms.ModelForm):
    """Форма для добавления одного изображения к объявлению"""
    class Meta:
        model = AdImage
        fields = ['image_file', 'image_url', 'is_main']
        widgets = {
            'image_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите URL изображения'
            }),            'is_main': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get('image_file')
        image_url = cleaned_data.get('image_url')
        
        # Если форма полностью пустая, это нормально (для формсета может быть пустая форма)
        if not image_file and not image_url:
            return cleaned_data
        
        # Если указаны оба варианта, показать ошибку
        if image_file and image_url:
            raise forms.ValidationError('Выберите либо файл, либо URL, но не оба варианта.')
          # Проверка размера файла
        if image_file and image_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 5MB.')
        
        # Проверка размеров изображения
        if image_file:
            try:
                from PIL import Image as PILImage
                img = PILImage.open(image_file)
                # Сохраняем позицию в файле для последующих операций
                image_file.seek(0)
                
                # Проверяем размеры
                max_size = 500
                if img.width > max_size or img.height > max_size:
                    # Масштабируем изображение до максимального размера
                    img.thumbnail((max_size, max_size))
                    
                    # Создаем временный файл для сохранения
                    import io
                    from django.core.files.uploadedfile import InMemoryUploadedFile
                    
                    output = io.BytesIO()
                    img_format = image_file.name.split('.')[-1].upper()
                    if img_format not in ['JPEG', 'JPG', 'PNG', 'GIF']:
                        img_format = 'JPEG'
                    
                    img.save(output, format=img_format)
                    output.seek(0)
                    
                    # Заменяем файл в cleaned_data на масштабированный
                    cleaned_data['image_file'] = InMemoryUploadedFile(
                        output,
                        'ImageField',
                        f"{image_file.name.split('.')[0]}.{img_format.lower()}",
                        f'image/{img_format.lower()}',
                        output.getbuffer().nbytes,
                        None
                    )
            except Exception as e:
                # Если не удалось обработать изображение, просто логируем ошибку
                import logging
                logging.getLogger('django').error(f"Ошибка обработки изображения: {e}")
        
        return cleaned_data


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Добавьте сообщение к предложению обмена...'
            }),
        }


class UserProfileForm(forms.ModelForm):
    use_default_avatar = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'default_avatar', 'phone_number', 'bio', 'city', 'birth_date', 'show_phone', 'show_email', 'show_full_name', 'show_birth_date']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'avatar-upload'
            }),
            'default_avatar': forms.RadioSelect(attrs={
                'class': 'avatar-radio'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш город'
            }),            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'show_phone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_full_name': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),            'show_birth_date': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.fields['default_avatar'].required = False
        self.fields['phone_number'].required = False
        self.fields['bio'].required = False
        self.fields['city'].required = False
        self.fields['birth_date'].required = False
          # Устанавливаем правильный формат для даты
        self.fields['birth_date'].input_formats = ['%Y-%m-%d']
        
    def clean(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get('avatar')
        use_default = cleaned_data.get('use_default_avatar')
        default_avatar = cleaned_data.get('default_avatar')
        
        if not avatar and not default_avatar:
            cleaned_data['default_avatar'] = 'default1.png'
            
        # Проверяем только если это новый файловый объект, а не существующий ImageFieldFile
        if avatar and hasattr(avatar, 'content_type'):
            if avatar.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Размер файла не должен превышать 5MB')
            if not avatar.content_type.startswith('image'):
                raise forms.ValidationError('Файл должен быть изображением')
                
        return cleaned_data
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            from datetime import date
            today = date.today()
            if birth_date > today:
                raise forms.ValidationError('Дата рождения не может быть в будущем')
            if birth_date.year < 1900:
                raise forms.ValidationError('Дата рождения не может быть раньше 1900 года')
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age > 120:
                raise forms.ValidationError('Возраст не может превышать 120 лет')
        return birth_date


class AdCommentForm(forms.ModelForm):
    """Форма для добавления комментариев к объявлениям"""
    
    class Meta:
        model = AdComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...',
                'maxlength': 1000
            })
        }
        labels = {
            'content': 'Комментарий'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True


class AdCommentReplyForm(forms.ModelForm):
    """Форма для ответов на комментарии"""
    
    class Meta:
        model = AdComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Написать ответ...',
                'maxlength': 1000
            })
        }
        labels = {
            'content': 'Ответ'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True


# Формсет для множественных изображений
from django.forms import formset_factory

# Создаем формсет для добавления до 5 изображений
AdImageFormSet = formset_factory(
    AdImageForm, 
    extra=0,  # Не показываем пустые формы по умолчанию
    max_num=5,  # Максимум 5 изображений
    validate_max=True,
    can_delete=True  # Позволяем удалять изображения
)


class PrivateMessageForm(forms.ModelForm):
    """Форма для отправки личных сообщений"""
    
    class Meta:
        model = PrivateMessage
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема сообщения'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваше сообщение...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = True
        self.fields['content'].required = True


class MessageReplyForm(forms.ModelForm):
    """Форма для ответа на сообщение"""
    
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш ответ...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True


class UserBlockForm(forms.ModelForm):
    """Форма для блокировки пользователя"""
    
    class Meta:
        model = UserBlock
        fields = ['reason']
        widgets = {
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Причина блокировки (необязательно)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].required = False
