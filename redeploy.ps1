# =============================================
# BIMEH - Redeploy automatico a Render
# =============================================
# Uso:
#   .\redeploy.ps1
#
# Configurar las variables de abajo antes de usar:

$RENDER_API_KEY = "TU_API_KEY_AQUI"     # Obtener en: dashboard.render.com/u/settings > API Keys
$SERVICE_ID     = "TU_SERVICE_ID_AQUI"  # Obtener ejecutando: Invoke-WebRequest -Uri "https://api.render.com/v1/services?limit=10" ...

# =============================================

$headers = @{
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Content-Type"  = "application/json"
    "Accept"        = "application/json"
}

Write-Host ""
Write-Host "  BIMEH - Redeploy a Render" -ForegroundColor Cyan
Write-Host "  Servicio: $SERVICE_ID" -ForegroundColor DarkCyan
Write-Host ""

# Disparar deploy con clear cache
$body = '{"clearCache": "clear"}'

try {
    $response = Invoke-WebRequest `
        -Uri "https://api.render.com/v1/services/$SERVICE_ID/deploys" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -UseBasicParsing

    $data = $response.Content | ConvertFrom-Json

    Write-Host "  Deploy iniciado correctamente!" -ForegroundColor Green
    Write-Host "  Deploy ID : $($data.id)" -ForegroundColor White
    Write-Host "  Estado    : $($data.status)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Esperando que el servidor quede Live..." -ForegroundColor Cyan

    $deployId = $data.id
    $maxWait = 40
    $attempts = 0

    do {
        Start-Sleep -Seconds 15
        $attempts++

        $statusRes = Invoke-WebRequest `
            -Uri "https://api.render.com/v1/services/$SERVICE_ID/deploys/$deployId" `
            -Headers $headers `
            -UseBasicParsing

        $statusData = $statusRes.Content | ConvertFrom-Json
        $currentStatus = $statusData.status

        $color = if ($currentStatus -eq "live") { "Green" }
                 elseif ($currentStatus -in @("build_failed","deactivated")) { "Red" }
                 else { "Yellow" }

        Write-Host "  [$attempts/$maxWait] Estado: $currentStatus" -ForegroundColor $color

    } while ($currentStatus -notin @("live", "build_failed", "deactivated") -and $attempts -lt $maxWait)

    if ($currentStatus -eq "live") {
        Write-Host ""
        Write-Host "  Deploy exitoso! La API esta Live en:" -ForegroundColor Green
        Write-Host "  https://bimeh-api.onrender.com" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "  El deploy termino con estado: $currentStatus" -ForegroundColor Red
        Write-Host "  Revisa los logs en dashboard.render.com" -ForegroundColor DarkGray
    }

} catch {
    Write-Host "  ERROR al iniciar el deploy: $_" -ForegroundColor Red
    Write-Host "  Verifica que RENDER_API_KEY y SERVICE_ID sean correctos." -ForegroundColor DarkGray
}

Write-Host ""
