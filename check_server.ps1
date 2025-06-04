# PowerShell скрипт для проверки готовности сервера
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== SERVER READINESS CHECK ===" -ForegroundColor Green
Write-Host "Checking server: 194.58.112.174" -ForegroundColor Yellow
Write-Host "Domain: swapsphere.ru" -ForegroundColor Yellow
Write-Host ""

# Проверка DNS
Write-Host "1. Checking DNS..." -ForegroundColor Cyan
try {
    $dns = Resolve-DnsName -Name "swapsphere.ru" -Type A -ErrorAction Stop
    if ($dns.IPAddress -eq "194.58.112.174") {
        Write-Host "   DNS: OK (swapsphere.ru -> 194.58.112.174)" -ForegroundColor Green
    } else {
        Write-Host "   DNS: WRONG IP ($($dns.IPAddress))" -ForegroundColor Red
    }
} catch {
    Write-Host "   DNS: FAILED" -ForegroundColor Red
}

# Проверка ping
Write-Host "2. Checking ping..." -ForegroundColor Cyan
$ping = Test-Connection -ComputerName 194.58.112.174 -Count 2 -Quiet
if ($ping) {
    Write-Host "   Ping: OK (server is online)" -ForegroundColor Green
} else {
    Write-Host "   Ping: FAILED (server offline or blocked)" -ForegroundColor Red
}

# Проверка SSH порта
Write-Host "3. Checking SSH port 22..." -ForegroundColor Cyan
$ssh = Test-NetConnection -ComputerName 194.58.112.174 -Port 22 -InformationLevel Quiet
if ($ssh) {
    Write-Host "   SSH: OK (port 22 is open)" -ForegroundColor Green
    Write-Host "   Ready to connect: ssh root@194.58.112.174" -ForegroundColor White
} else {
    Write-Host "   SSH: FAILED (port 22 is closed)" -ForegroundColor Red
    Write-Host "   Need to configure SSH in reg.ru panel" -ForegroundColor Yellow
}

# Проверка HTTP портов
Write-Host "4. Checking web ports..." -ForegroundColor Cyan
$http = Test-NetConnection -ComputerName 194.58.112.174 -Port 80 -InformationLevel Quiet
$https = Test-NetConnection -ComputerName 194.58.112.174 -Port 443 -InformationLevel Quiet

if ($http) {
    Write-Host "   HTTP (80): OK" -ForegroundColor Green
} else {
    Write-Host "   HTTP (80): CLOSED" -ForegroundColor Yellow
}

if ($https) {
    Write-Host "   HTTPS (443): OK" -ForegroundColor Green
} else {
    Write-Host "   HTTPS (443): CLOSED" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Green

if ($ssh) {
    Write-Host "✅ SERVER IS READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run: ssh root@194.58.112.174" -ForegroundColor White
    Write-Host "2. Execute deployment commands" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run automated deployment:" -ForegroundColor Yellow
    Write-Host ".\connect_server.ps1" -ForegroundColor White
} else {
    Write-Host "❌ SERVER NEEDS CONFIGURATION" -ForegroundColor Red
    Write-Host ""
    Write-Host "Actions needed:" -ForegroundColor Yellow
    Write-Host "1. Login to reg.ru panel: https://www.reg.ru/user/account" -ForegroundColor White
    Write-Host "2. Check server status (should be ON)" -ForegroundColor White
    Write-Host "3. Enable SSH access" -ForegroundColor White
    Write-Host "4. Set root password" -ForegroundColor White
    Write-Host ""
    Write-Host "See: SERVER_SETUP_ISSUE.md for detailed instructions" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Reg.ru credentials:" -ForegroundColor Cyan
Write-Host "Login: vovapilip46@gmail.com" -ForegroundColor White
Write-Host "Password: 59Ofavoh" -ForegroundColor White
