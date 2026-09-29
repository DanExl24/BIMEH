@echo off
title Tunel Cloudflare - Ollama BIMEH
echo ========================================================
echo       INICIANDO TUNEL CLOUDFLARE PARA OLLAMA BIMEH
echo ========================================================
echo.
echo Asegurese de que Ollama este ejecutandose en segundo plano.
echo Este tunel creara una URL segura https://...trycloudflare.com
echo Copie dicha URL y peguela en el icono de tuerca del panel de IA de BIMEH.
echo.
echo Presione Ctrl + C para detener el tunel cuando no lo necesite.
echo ========================================================
echo.

set OLLAMA_ORIGINS=*
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:11434 --http-host-header localhost

pause
