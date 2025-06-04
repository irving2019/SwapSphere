# PowerShell скрипт для подключения к серверу
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Connecting to swapsphere.ru server" -ForegroundColor Green
Write-Host "Reg.ru login: vovapilip46@gmail.com" -ForegroundColor Yellow
Write-Host "Reg.ru password: 59Ofavoh" -ForegroundColor Yellow
Write-Host "Server IP: 194.58.112.174" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия SSH клиента
if (Get-Command ssh -ErrorAction SilentlyContinue) {
    Write-Host "SSH client found. Connecting to server..." -ForegroundColor Green
    Write-Host "Commands to run after connecting:" -ForegroundColor Yellow
    Write-Host "1. apt update && apt upgrade -y" -ForegroundColor White
    Write-Host "2. curl -fsSL https://get.docker.com | sh" -ForegroundColor White
    Write-Host "3. git clone https://github.com/vovastar/SwapSphere.git" -ForegroundColor White
    Write-Host "4. cd SwapSphere && cp .env.production .env" -ForegroundColor White
    Write-Host "5. chmod +x deploy_swapsphere_ru.sh && ./deploy_swapsphere_ru.sh" -ForegroundColor White
    Write-Host ""
    ssh root@194.58.112.174
} else {
    Write-Host "SSH client not found!" -ForegroundColor Red
    Write-Host "Install OpenSSH or use PuTTY" -ForegroundColor Yellow
    Write-Host "Connection data:" -ForegroundColor Cyan
    Write-Host "   Host: 194.58.112.174" -ForegroundColor White
    Write-Host "   Port: 22" -ForegroundColor White
    Write-Host "   User: root" -ForegroundColor White
}
