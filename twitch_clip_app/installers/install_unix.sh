#!/bin/bash
# Скрипт установки Twitch Clip Generator Pro для macOS/Linux

echo "============================================"
echo "  Twitch Clip Generator Pro - Установка"
echo "============================================"
echo ""

# Проверка Python
echo "[1/5] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    echo "Установите Python 3.8+"
    exit 1
fi
echo "✓ Python установлен: $(python3 --version)"

# Проверка FFmpeg
echo ""
echo "[2/5] Проверка FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "ПРЕДУПРЕЖДЕНИЕ: FFmpeg не найден!"
    echo "Без FFmpeg программа не сможет обрабатывать видео"
    echo ""
    read -p "Установить FFmpeg? (y/n): " install_ffmpeg
    if [ "$install_ffmpeg" = "y" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Установка через Homebrew..."
            brew install ffmpeg
        else
            echo "Установка через apt..."
            sudo apt update && sudo apt install -y ffmpeg
        fi
    fi
else
    echo "✓ FFmpeg установлен: $(ffmpeg -version | head -n1)"
fi

# Создание виртуального окружения
echo ""
echo "[3/5] Создание виртуального окружения..."
if [ -d "venv" ]; then
    echo "Виртуальное окружение уже существует"
else
    python3 -m venv venv
    echo "✓ Виртуальное окружение создано"
fi

# Активация и установка зависимостей
echo ""
echo "[4/5] Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ОШИБКА при установке зависимостей!"
    exit 1
fi
echo "✓ Зависимости установлены"

# Создание ярлыка
echo ""
echo "[5/5] Создание ярлыка..."
cat > "Запустить_TwitchClipGenerator.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python src/gui.py "$@"
EOF
chmod +x "Запустить_TwitchClipGenerator.sh"
echo "✓ Ярлык создан"

echo ""
echo "============================================"
echo "  Установка завершена успешно!"
echo "============================================"
echo ""
echo "Для запуска программы:"
echo "1. Запустите: ./Запустить_TwitchClipGenerator.sh"
echo "2. Или выполните: python src/gui.py"
echo ""
echo "Документация: README.md"
echo ""
