# Скрипт установки Twitch Clip Generator Pro для Windows
# Запустите этот файл для автоматической установки

@echo off
chcp 65001 >nul
echo ============================================
echo   Twitch Clip Generator Pro - Установка
echo ============================================
echo.

REM Проверка Python
echo [1/5] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Скачайте и установите Python с python.org
    echo Не забудьте поставить галочку "Add Python to PATH"
    pause
    exit /b 1
)
echo ✓ Python установлен

REM Проверка FFmpeg
echo.
echo [2/5] Проверка FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПРЕДУПРЕЖДЕНИЕ: FFmpeg не найден!
    echo Без FFmpeg программа не сможет обрабатывать видео
    echo.
    echo Хотите установить FFmpeg автоматически?
    set /p install_ffmpeg="Y/N: "
    if /i "%install_ffmpeg%"=="Y" (
        echo Загрузка FFmpeg...
        REM Здесь можно добавить автоматическую загрузку FFmpeg
        echo Перейдите на ffmpeg.org для ручной установки
    )
) else (
    echo ✓ FFmpeg установлен
)

REM Создание виртуального окружения
echo.
echo [3/5] Создание виртуального окружения...
if exist "venv" (
    echo Виртуальное окружение уже существует
) else (
    python -m venv venv
    echo ✓ Виртуальное окружение создано
)

REM Активация и установка зависимостей
echo.
echo [4/5] Установка зависимостей...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА при установке зависимостей!
    pause
    exit /b 1
)
echo ✓ Зависимости установлены

REM Создание ярлыка
echo.
echo [5/5] Создание ярлыка...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo call venv\Scripts\activate.bat
echo python src\gui.py %%*
echo pause
) > "Запустить_TwitchClipGenerator.bat"

echo ✓ Ярлык создан

echo.
echo ============================================
echo   Установка завершена успешно!
echo ============================================
echo.
echo Для запуска программы:
echo 1. Дважды кликните на "Запустить_TwitchClipGenerator.bat"
echo 2. Или выполните: python src/gui.py
echo.
echo Документация: README.md
echo.
pause
