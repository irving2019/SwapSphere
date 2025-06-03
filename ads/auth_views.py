from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib import messages

def logout_view(request):
    """Простое представление для выхода, поддерживающее GET и POST запросы"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'До свидания, {username}! Вы успешно вышли из системы.')
    return redirect('/')
