#!/bin/bash
# Подключение к серверу и развертывание SwapSphere

echo "🌐 Подключение к серверу swapsphere.ru (194.58.112.174)"
echo "📧 Данные для входа: root@194.58.112.174"
echo ""

# Проверка SSH ключей
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "🔑 Генерирую SSH ключ..."
    ssh-keygen -t rsa -b 4096 -C "vovapilip46@gmail.com" -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH ключ создан"
    echo "📋 Публичный ключ для добавления на сервер:"
    cat ~/.ssh/id_rsa.pub
    echo ""
    echo "⚠️ Добавьте этот ключ в ~/.ssh/authorized_keys на сервере"
    read -p "Нажмите Enter после добавления ключа на сервер..."
fi

# Подключение к серверу
echo "🔌 Подключаюсь к серверу..."
ssh -o StrictHostKeyChecking=no root@194.58.112.174 << 'ENDSSH'
    echo "✅ Подключение к серверу установлено!"
    echo "🖥️ Информация о сервере:"
    echo "   OS: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/redhat-release 2>/dev/null || echo "Unknown")"
    echo "   Kernel: $(uname -r)"
    echo "   CPU: $(nproc) cores"
    echo "   RAM: $(free -h | awk '/^Mem:/ {print $2}')"
    echo "   Disk: $(df -h / | awk 'NR==2 {print $4}') free"
    echo ""
    
    # Обновление системы
    echo "📦 Обновляю систему..."
    if command -v apt &> /dev/null; then
        apt update && apt upgrade -y
        apt install -y git curl wget unzip
    elif command -v yum &> /dev/null; then
        yum update -y
        yum install -y git curl wget unzip
    fi
    
    # Создание пользователя для развертывания
    echo "👤 Создаю пользователя swapsphere..."
    if ! id "swapsphere" &>/dev/null; then
        useradd -m -s /bin/bash swapsphere
        usermod -aG sudo swapsphere
        # Копирование SSH ключей
        mkdir -p /home/swapsphere/.ssh
        cp ~/.ssh/authorized_keys /home/swapsphere/.ssh/
        chown -R swapsphere:swapsphere /home/swapsphere/.ssh
        chmod 700 /home/swapsphere/.ssh
        chmod 600 /home/swapsphere/.ssh/authorized_keys
    fi
    
    # Установка Docker
    echo "🐳 Проверяю Docker..."
    if ! command -v docker &> /dev/null; then
        echo "📦 Устанавливаю Docker..."
        curl -fsSL https://get.docker.com | sh
        usermod -aG docker swapsphere
        systemctl enable docker
        systemctl start docker
    fi
    
    # Клонирование репозитория
    echo "📂 Клонирую проект SwapSphere..."
    cd /home/swapsphere
    if [ ! -d "SwapSphere" ]; then
        git clone https://github.com/vovastar/SwapSphere.git
        chown -R swapsphere:swapsphere SwapSphere
    fi
    
    echo "✅ Сервер готов к развертыванию!"
    echo ""
    echo "🚀 Для развертывания выполните:"
    echo "   su - swapsphere"
    echo "   cd SwapSphere"
    echo "   chmod +x deploy_swapsphere_ru.sh"
    echo "   ./deploy_swapsphere_ru.sh"
ENDSSH

echo ""
echo "✅ Настройка сервера завершена!"
echo "🔗 Теперь подключитесь как пользователь swapsphere:"
echo "   ssh swapsphere@194.58.112.174"
echo ""
echo "🚀 И запустите развертывание:"
echo "   cd SwapSphere"
echo "   ./deploy_swapsphere_ru.sh"
