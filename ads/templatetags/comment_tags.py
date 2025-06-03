from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()

@register.filter
def can_delete_comment(comment, user):
    """Проверяет, может ли пользователь удалить комментарий"""
    if isinstance(user, AnonymousUser):
        return False
    return comment.can_delete(user)

@register.filter 
def can_reply_comment(comment, user):
    """Проверяет, может ли пользователь ответить на комментарий"""
    if isinstance(user, AnonymousUser):
        return False
    return comment.can_reply(user)
