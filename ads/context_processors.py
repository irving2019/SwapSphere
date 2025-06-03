"""
Контекстные процессоры для приложения ads
"""
from .models import Conversation, ExchangeProposal


def unread_messages(request):
    """
    Добавляет количество непрочитанных сообщений в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        # Подсчет непрочитанных сообщений
        unread_count = 0
        conversations = Conversation.objects.filter(
            participants=request.user
        ).distinct()
        
        for conversation in conversations:
            unread_count += conversation.get_unread_count(request.user)
          # Подсчет непрочитанных предложений
        unread_proposals = ExchangeProposal.objects.filter(
            ad_receiver__user=request.user,
            is_read_by_receiver=False
        ).count()
        
        return {
            'unread_messages_count': unread_count,
            'unread_proposals_count': unread_proposals,
        }
    
    return {
        'unread_messages_count': 0,
        'unread_proposals_count': 0,
    }
