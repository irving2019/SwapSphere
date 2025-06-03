/**
 * Система уведомлений для SwapSphere
 * Автоматически обновляет счетчики непрочитанных сообщений
 */

class NotificationSystem {
    constructor() {
        this.updateInterval = 30000; // 30 секунд
        this.isActive = true;
        this.lastUpdate = Date.now();
        
        this.init();
    }
    
    init() {
        // Запуск только если пользователь авторизован
        if (!document.querySelector('.nav-link.messages-link')) {
            return;
        }
        
        // Обработка видимости страницы
        document.addEventListener('visibilitychange', () => {
            this.isActive = !document.hidden;
            if (this.isActive) {
                this.updateNotifications();
            }
        });
        
        // Периодическое обновление
        setInterval(() => {
            if (this.isActive) {
                this.updateNotifications();
            }
        }, this.updateInterval);
        
        // Обновление при загрузке страницы
        this.updateNotifications();
    }
    
    async updateNotifications() {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateBadges(data);
            }
        } catch (error) {
            console.log('Ошибка обновления уведомлений:', error);
        }
    }
    
    updateBadges(data) {
        const messagesLink = document.querySelector('.nav-link.messages-link');
        if (!messagesLink) return;
        
        // Обновление значка сообщений
        let existingBadge = messagesLink.querySelector('.badge');
        
        if (data.unread_messages_count > 0) {
            const badgeText = data.unread_messages_count > 99 ? '99+' : data.unread_messages_count;
            
            if (existingBadge) {
                existingBadge.textContent = badgeText;
            } else {
                const badge = document.createElement('span');
                badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
                badge.style.cssText = 'font-size: 0.65em; min-width: 20px; height: 20px; display: flex; align-items: center; justify-content: center;';
                badge.innerHTML = `${badgeText}<span class="visually-hidden">непрочитанные сообщения</span>`;
                messagesLink.appendChild(badge);
            }
            
            // Анимация при новых сообщениях
            if (data.unread_messages_count > this.lastUnreadCount) {
                this.animateNewNotification(messagesLink);
            }
        } else if (existingBadge) {
            existingBadge.remove();
        }
        
        // Обновление заголовка страницы
        this.updatePageTitle(data.unread_messages_count);
        
        this.lastUnreadCount = data.unread_messages_count;
    }
    
    updatePageTitle(unreadCount) {
        const originalTitle = document.title.replace(/^\(\d+\) /, '');
        
        if (unreadCount > 0) {
            document.title = `(${unreadCount}) ${originalTitle}`;
        } else {
            document.title = originalTitle;
        }
    }
    
    animateNewNotification(element) {
        // Пульсация
        element.style.animation = 'none';
        element.offsetHeight; // Триггер reflow
        element.style.animation = 'pulse 0.6s ease-in-out 3';
        
        // Добавление CSS если его нет
        if (!document.querySelector('#notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
    
    // Показ браузерного уведомления (требует разрешения)
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }
    
    showBrowserNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png',
                tag: 'swapsphere-message'
            });
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    window.notificationSystem = new NotificationSystem();
});
