@echo off
echo ==========================================
echo    INICIANDO ESTACIONAMENTO INTELIGENTE
echo ==========================================

:: Entra na pasta onde o .bat está guardado e fixa-a como diretório base
cd /d "%~dp0"

echo [1/3] Verificando ficheiros de modulo (__init__.py)...
if not exist "gateway\__init__.py" type nul > "gateway\__init__.py"
if not exist "sensores\__init__.py" type nul > "sensores\__init__.py"
if not exist "cliente\__init__.py" type nul > "cliente\__init__.py"
if not exist "generated\__init__.py" type nul > "generated\__init__.py"

echo [2/3] Verificando Ambiente Virtual (.venv)...
if not exist ".venv\Scripts\activate.bat" (
    echo Ambiente virtual nao encontrado! Criando a .venv agora com 'py'...
    py -m venv .venv
    call .venv\Scripts\activate.bat
    pip install protobuf grpcio-tools
)

echo [3/3] Verificando PHP Portatil...
set "PHP_DIR=%~dp0php_bin"
set "PHP_ZIP=%~dp0php.zip"

if not exist "%PHP_DIR%\php.exe" (
    echo Baixando PHP Portatil direto do servidor oficial ^(isso pode levar alguns segundos^)...
    curl -L -o "%PHP_ZIP%" "https://windows.php.net/downloads/releases/archives/php-8.2.10-nts-Win32-vs16-x64.zip"

    echo Extraindo ficheiros...
    mkdir "%PHP_DIR%"
    tar -xf "%PHP_ZIP%" -C "%PHP_DIR%"

    echo Limpando instalador...
    del "%PHP_ZIP%"
    echo PHP Portatil pronto para utilizacao!
) else (
    echo PHP Portatil ja configurado na pasta do projeto.
)

echo.
echo Iniciando os Sensores (Preparando os ouvidos)...
start "Sensor Estacionamento" cmd /k "call .venv\Scripts\activate && set PYTHONPATH=. && py -m sensores.sensor_estaciona"
start "Sensor Fluxo" cmd /k "call .venv\Scripts\activate && set PYTHONPATH=. && py -m sensores.sensor_fluxo"
start "Sensor Cancela" cmd /k "call .venv\Scripts\activate && set PYTHONPATH=. && py -m sensores.sensor_cancela"

:: Aguarda 3 segundos
timeout /t 3 /nobreak > nul

echo Iniciando o Gateway...
start "Gateway" cmd /k "call .venv\Scripts\activate && set PYTHONPATH=. && py -m gateway.gateway"

:: Aguarda 5 segundos
timeout /t 5 /nobreak > nul

echo Iniciando o Cliente...
start "Cliente Analitico" cmd /k "call .venv\Scripts\activate && set PYTHONPATH=. && py -m cliente.cliente"

echo Iniciando o Painel Web (PHP Portatil com SQLite)...
start "Painel Web" cmd /k "cd /d "%~dp0painel" && "%PHP_DIR%\php.exe" -d extension_dir="%PHP_DIR%\ext" -d extension=sqlite3 -S localhost:8080"

echo.
echo Tudo aberto com sucesso! Aceda a http://localhost:8080
pause