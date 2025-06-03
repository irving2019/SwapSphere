#!/bin/bash

# 🚀 SwapSphere - Скрипт автоматического развертывания
# Этот скрипт настраивает и запускает SwapSphere проект

set -e  # Выход при ошибке

echo "🔄 SwapSphere - Автоматическое развертывание"
echo "============================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка системных требований
check_requirements() {
    print_status "Проверка системных требований..."
    
    # Проверка Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        print_success "Python $PYTHON_VERSION найден"
    else
        print_error "Python 3 не найден. Установите Python 3.8+"
        exit 1
    fi
    
    # Проверка pip
    if command -v pip3 &> /dev/null; then
        print_success "pip найден"
    else
        print_error "pip не найден. Установите pip"
        exit 1
    fi
    
    # Проверка Docker (опционально)
    if command -v docker &> /dev/null; then
        print_success "Docker найден"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker не найден. Будет использована локальная установка"
        DOCKER_AVAILABLE=false
    fi
}

# Создание виртуального окружения
setup_venv() {
    print_status "Настройка виртуального окружения..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_warning "Виртуальное окружение уже существует"
    fi
    
    # Активация виртуального окружения
    source venv/bin/activate
    print_success "Виртуальное окружение активировано"
    
    # Обновление pip
    pip install --upgrade pip
    print_success "pip обновлен"
}

# Установка зависимостей
install_dependencies() {
    print_status "Установка зависимостей..."
    
    pip install -r requirements.txt
    print_success "Зависимости установлены"
}

# Настройка базы данных
setup_database() {
    print_status "Настройка базы данных..."
    
    # Применение миграций
    python manage.py migrate
    print_success "Миграции применены"
    
    # Создание суперпользователя (если нужно)
    echo "Создать суперпользователя? (y/n):"
    read -r CREATE_SUPERUSER
    if [ "$CREATE_SUPERUSER" = "y" ] || [ "$CREATE_SUPERUSER" = "Y" ]; then
        python manage.py createsuperuser
        print_success "Суперпользователь создан"
    fi
}

# Сбор статических файлов
collect_static() {
    print_status "Сбор статических файлов..."
    
    python manage.py collectstatic --noinput
    print_success "Статические файлы собраны"
}

# Запуск тестов
run_tests() {
    print_status "Запуск тестов..."
    
    python test_full_autotest.py
    if [ $? -eq 0 ]; then
        print_success "Все тесты прошли успешно"
    else
        print_warning "Некоторые тесты не прошли. Проверьте логи"
    fi
}

# Запуск сервера разработки
start_development_server() {
    print_status "Запуск сервера разработки..."
    
    print_success "SwapSphere готов к использованию!"
    print_status "Сервер доступен по адресу: http://127.0.0.1:8000"
    print_status "Админ-панель: http://127.0.0.1:8000/admin/"
    
    python manage.py runserver
}

# Docker развертывание
deploy_with_docker() {
    print_status "Развертывание с Docker..."
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo "Выберите режим:"
        echo "1) Разработка (docker-compose.dev.yml)"
        echo "2) Продакшн (docker-compose.yml)"
        read -r DOCKER_MODE
        
        if [ "$DOCKER_MODE" = "1" ]; then
            docker-compose -f docker-compose.dev.yml up --build
        else
            docker-compose up --build
        fi
    else
        print_error "Docker не доступен"
        exit 1
    fi
}

# Главное меню
main_menu() {
    echo ""
    echo "Выберите режим развертывания:"
    echo "1) Локальная разработка"
    echo "2) Docker (разработка)"
    echo "3) Docker (продакшн)"
    echo "4) Только тесты"
    read -r DEPLOYMENT_MODE
    
    case $DEPLOYMENT_MODE in
        1)
            check_requirements
            setup_venv
            install_dependencies
            setup_database
            collect_static
            run_tests
            start_development_server
            ;;
        2)
            check_requirements
            DOCKER_AVAILABLE=true
            deploy_with_docker
            ;;
        3)
            check_requirements
            DOCKER_AVAILABLE=true
            deploy_with_docker
            ;;
        4)
            check_requirements
            setup_venv
            install_dependencies
            run_tests
            ;;
        *)
            print_error "Неверный выбор"
            exit 1
            ;;
    esac
}

# Запуск главного меню
main_menu
