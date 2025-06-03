# 🚀 SwapSphere - Скрипт автоматического развертывания для Windows
# PowerShell скрипт для настройки и запуска SwapSphere проекта

param(
    [string]$Mode = "menu"
)

# Цвета для вывода
$Global:Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Global:Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Global:Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Global:Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Global:Colors.Red
}

function Test-SystemRequirements {
    Write-Status "Проверка системных требований..."
    
    # Проверка Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            Write-Success "Python $($matches[1]) найден"
            $Global:PythonAvailable = $true
        }
    }
    catch {
        Write-Error "Python не найден. Установите Python 3.8+"
        exit 1
    }
    
    # Проверка pip
    try {
        pip --version | Out-Null
        Write-Success "pip найден"
    }
    catch {
        Write-Error "pip не найден. Установите pip"
        exit 1
    }
    
    # Проверка Docker
    try {
        docker --version | Out-Null
        Write-Success "Docker найден"
        $Global:DockerAvailable = $true
    }
    catch {
        Write-Warning "Docker не найден. Будет использована локальная установка"
        $Global:DockerAvailable = $false
    }
}

function Initialize-VirtualEnvironment {
    Write-Status "Настройка виртуального окружения..."
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Success "Виртуальное окружение создано"
    }
    else {
        Write-Warning "Виртуальное окружение уже существует"
    }
    
    # Активация виртуального окружения
    & ".\venv\Scripts\Activate.ps1"
    Write-Success "Виртуальное окружение активировано"
    
    # Обновление pip
    python -m pip install --upgrade pip
    Write-Success "pip обновлен"
}

function Install-Dependencies {
    Write-Status "Установка зависимостей..."
    
    pip install -r requirements.txt
    Write-Success "Зависимости установлены"
}

function Initialize-Database {
    Write-Status "Настройка базы данных..."
    
    # Применение миграций
    python manage.py migrate
    Write-Success "Миграции применены"
    
    # Создание суперпользователя
    $createSuperuser = Read-Host "Создать суперпользователя? (y/n)"
    if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
        python manage.py createsuperuser
        Write-Success "Суперпользователь создан"
    }
}

function Invoke-CollectStatic {
    Write-Status "Сбор статических файлов..."
    
    python manage.py collectstatic --noinput
    Write-Success "Статические файлы собраны"
}

function Invoke-Tests {
    Write-Status "Запуск тестов..."
    
    $testResult = python test_full_autotest.py
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Все тесты прошли успешно"
    }
    else {
        Write-Warning "Некоторые тесты не прошли. Проверьте логи"
    }
    return $LASTEXITCODE -eq 0
}

function Start-DevelopmentServer {
    Write-Status "Запуск сервера разработки..."
    
    Write-Success "SwapSphere готов к использованию!"
    Write-Status "Сервер доступен по адресу: http://127.0.0.1:8000"
    Write-Status "Админ-панель: http://127.0.0.1:8000/admin/"
    Write-Host ""
    Write-Host "Нажмите Ctrl+C для остановки сервера" -ForegroundColor $Global:Colors.Cyan
    
    python manage.py runserver
}

function Start-DockerDeployment {
    Write-Status "Развертывание с Docker..."
    
    if ($Global:DockerAvailable) {
        Write-Host "Выберите режим:"
        Write-Host "1) Разработка (docker-compose.dev.yml)"
        Write-Host "2) Продакшн (docker-compose.yml)"
        $dockerMode = Read-Host "Введите номер"
        
        if ($dockerMode -eq "1") {
            docker-compose -f docker-compose.dev.yml up --build
        }
        else {
            docker-compose up --build
        }
    }
    else {
        Write-Error "Docker не доступен"
        exit 1
    }
}

function Show-MainMenu {
    Write-Host ""
    Write-Host "🔄 SwapSphere - Автоматическое развертывание" -ForegroundColor $Global:Colors.Cyan
    Write-Host "=============================================" -ForegroundColor $Global:Colors.Cyan
    Write-Host ""
    Write-Host "Выберите режим развертывания:"
    Write-Host "1) Локальная разработка"
    Write-Host "2) Docker (разработка)"
    Write-Host "3) Docker (продакшн)"
    Write-Host "4) Только тесты"
    Write-Host "5) Быстрый запуск (пропустить тесты)"
    
    $choice = Read-Host "Введите номер"
    
    switch ($choice) {
        "1" {
            Test-SystemRequirements
            Initialize-VirtualEnvironment
            Install-Dependencies
            Initialize-Database
            Invoke-CollectStatic
            Invoke-Tests
            Start-DevelopmentServer
        }
        "2" {
            Test-SystemRequirements
            Start-DockerDeployment
        }
        "3" {
            Test-SystemRequirements
            Start-DockerDeployment
        }
        "4" {
            Test-SystemRequirements
            Initialize-VirtualEnvironment
            Install-Dependencies
            Invoke-Tests
        }
        "5" {
            Test-SystemRequirements
            Initialize-VirtualEnvironment
            Install-Dependencies
            Initialize-Database
            Invoke-CollectStatic
            Start-DevelopmentServer
        }
        default {
            Write-Error "Неверный выбор"
            exit 1
        }
    }
}

# Главная функция
function Main {
    try {
        if ($Mode -eq "menu") {
            Show-MainMenu
        }
        elseif ($Mode -eq "test") {
            Test-SystemRequirements
            Initialize-VirtualEnvironment
            Install-Dependencies
            Invoke-Tests
        }
        elseif ($Mode -eq "dev") {
            Test-SystemRequirements
            Initialize-VirtualEnvironment
            Install-Dependencies
            Initialize-Database
            Invoke-CollectStatic
            Start-DevelopmentServer
        }
        else {
            Show-MainMenu
        }
    }
    catch {
        Write-Error "Произошла ошибка: $_"
        exit 1
    }
}

# Запуск
Main
