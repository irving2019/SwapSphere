# PowerShell скрипт для подключения к серверу

Write-Host "🌐 Подключение к серверу swapsphere.ru" -ForegroundColor Green
Write-Host "📧 Логин рег.ру: vovapilip46@gmail.com" -ForegroundColor Yellow
Write-Host "🔑 Пароль рег.ру: 59Ofavoh" -ForegroundColor Yellow
Write-Host "🖥️ IP сервера: 194.58.112.174" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия SSH клиента
if (Get-Command ssh -ErrorAction SilentlyContinue) {
    Write-Host "🔗 Подключаюсь к серверу..." -ForegroundColor Green
    ssh root@194.58.112.174
} else {
    Write-Host "❌ SSH клиент не найден!" -ForegroundColor Red
    Write-Host "💡 Установите OpenSSH или используйте PuTTY" -ForegroundColor Yellow
    Write-Host "🔗 Данные для подключения:" -ForegroundColor Cyan
    Write-Host "   Хост: 194.58.112.174" -ForegroundColor White
    Write-Host "   Порт: 22" -ForegroundColor White
    Write-Host "   Пользователь: root" -ForegroundColor White
}
