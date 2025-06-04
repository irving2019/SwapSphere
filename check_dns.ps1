# PowerShell script for checking DNS settings of swapsphere.ru
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "DNS settings check for swapsphere.ru" -ForegroundColor Green
Write-Host "Expected IP: 194.58.112.174" -ForegroundColor Yellow
Write-Host ""

# Проверка основного домена
Write-Host "🔍 Проверяю swapsphere.ru..." -ForegroundColor Cyan
try {
    $result1 = Resolve-DnsName -Name "swapsphere.ru" -Type A -ErrorAction Stop
    $ip1 = $result1.IPAddress
    if ($ip1 -eq "194.58.112.174") {
        Write-Host "✅ swapsphere.ru → $ip1 (ПРАВИЛЬНО)" -ForegroundColor Green
    } else {
        Write-Host "❌ swapsphere.ru → $ip1 (НЕПРАВИЛЬНО, ожидается 194.58.112.174)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ swapsphere.ru → НЕ РЕЗОЛВИТСЯ" -ForegroundColor Red
}

# Проверка www поддомена  
Write-Host "🔍 Проверяю www.swapsphere.ru..." -ForegroundColor Cyan
try {
    $result2 = Resolve-DnsName -Name "www.swapsphere.ru" -Type A -ErrorAction Stop
    $ip2 = $result2.IPAddress
    if ($ip2 -eq "194.58.112.174") {
        Write-Host "✅ www.swapsphere.ru → $ip2 (ПРАВИЛЬНО)" -ForegroundColor Green
    } else {
        Write-Host "❌ www.swapsphere.ru → $ip2 (НЕПРАВИЛЬНО, ожидается 194.58.112.174)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ www.swapsphere.ru → НЕ РЕЗОЛВИТСЯ" -ForegroundColor Red
}

# Проверка DNS серверов
Write-Host ""
Write-Host "🔍 Проверяю DNS-серверы..." -ForegroundColor Cyan
try {
    $ns = Resolve-DnsName -Name "swapsphere.ru" -Type NS -ErrorAction Stop
    Write-Host "📡 DNS-серверы для swapsphere.ru:" -ForegroundColor Yellow
    foreach ($server in $ns) {
        if ($server.NameHost -like "*reg.ru") {
            Write-Host "✅ $($server.NameHost)" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $($server.NameHost) (не рег.ру)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Не удалось получить DNS-серверы" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌐 Проверка в браузере:" -ForegroundColor Cyan
Write-Host "   • http://swapsphere.ru" -ForegroundColor White
Write-Host "   • https://swapsphere.ru" -ForegroundColor White

Write-Host ""
Write-Host "📋 Онлайн проверка DNS:" -ForegroundColor Yellow
Write-Host "   • https://dnschecker.org" -ForegroundColor White
Write-Host "   • https://www.whatsmydns.net" -ForegroundColor White

Write-Host ""
if ($ip1 -eq "194.58.112.174" -and $ip2 -eq "194.58.112.174") {
    Write-Host "🎉 DNS настроен ПРАВИЛЬНО! Можно развертывать сайт." -ForegroundColor Green
} else {
    Write-Host "⚠️ DNS настроен НЕПРАВИЛЬНО. Проверь настройки в панели рег.ру." -ForegroundColor Yellow
    Write-Host "📖 Смотри инструкцию: DNS_SETUP_GUIDE.md" -ForegroundColor Cyan
}
