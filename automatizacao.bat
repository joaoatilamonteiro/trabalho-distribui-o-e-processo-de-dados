@echo off
echo ==========================================
echo    INICIANDO ESTACIONAMENTO INTELIGENTE
echo ==========================================

set "DIR=%~dp0"

echo Iniciando os Sensores (Preparando os ouvidos)...
start "Sensor Estacionamento" cmd /k "cd /d "%DIR%" && call .venv\Scripts\activate && python -m sensores.sensor_estaciona"
start "Sensor Fluxo" cmd /k "cd /d "%DIR%" && call .venv\Scripts\activate && python -m sensores.sensor_fluxo"
start "Sensor Cancela" cmd /k "cd /d "%DIR%" && call .venv\Scripts\activate && python -m sensores.sensor_cancela"

:: Aguarda 3 segundos para garantir que todos os sensores estão rodando
timeout /t 3 /nobreak > nul

echo Iniciando o Gateway (Ele vai gritar agora!)...
start "Gateway" cmd /k "cd /d "%DIR%" && call .venv\Scripts\activate && python -m gateway.gateway"

:: Aguarda 1 segundo
timeout /t 5 /nobreak > nul

echo Iniciando o Cliente...
start "Cliente Analitico" cmd /k "cd /d "%DIR%" && call .venv\Scripts\activate && python -m cliente.cliente"

echo Tudo aberto com sucesso! Pode fechar esta janela principal.