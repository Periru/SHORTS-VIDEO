# Twitch Clip Generator - Быстрый старт

## 🚀 Установка за 5 минут

### Шаг 1: Установка системных зависимостей

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg python3-dev cmake

# macOS
brew install ffmpeg
```

### Шаг 2: Установка Python-зависимостей

```bash
cd /workspace
pip install -r requirements.txt
```

### Шаг 3: Проверка установки

```bash
python main.py --help
```

## 📋 Базовое использование

### Обработка локального видеофайла

```bash
python main.py --input "path/to/video.mp4" --duration 60 --max-clips 5
```

### Загрузка с Twitch (требуется настройка API)

1. Получите Client ID и OAuth токен на [Twitch Developer Console](https://dev.twitch.tv/)
2. Обновите `config.yaml`:
   ```yaml
   twitch:
     client_id: "your_client_id"
     oauth_token: "your_oauth_token"
   ```

3. Запустите:
   ```bash
   python main.py --channel "shroud" --video_id "1234567890"
   ```

## ⚙️ Настройки

### Основные параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--channel` | Имя Twitch канала | - |
| `--video_id` | ID VOD с Twitch | - |
| `--input` | Путь к локальному файлу | - |
| `--duration` | Длительность клипа (сек) | 60 |
| `--max-clips` | Макс. количество клипов | 5 |
| `--output-format` | vertical/square/horizontal | vertical |
| `--config` | Путь к config.yaml | config.yaml |

### Отключение функций

```bash
# Без анализа аудио
python main.py --input video.mp4 --no-audio-analysis

# Без анализа чата
python main.py --input video.mp4 --no-chat-analysis

# Без детекции эмоций
python main.py --input video.mp4 --no-emotion-detection

# Без субтитров
python main.py --input video.mp4 --no-subtitles
```

## 🎯 Как это работает

1. **Анализ аудио** - ищет пики громкости, смех, крики
2. **Анализ чата** - обнаруживает всплески активности, хайповые эмодзи
3. **Детекция эмоций** - находит эмоциональные реакции стримера
4. **Композитный скоринг** - объединяет все метрики
5. **Нарезка** - создаёт вертикальные клипы 9:16
6. **Субтитры** - автогенерация через Whisper

## 📁 Структура проекта

```
/workspace/
├── main.py              # Точка входа
├── config.yaml          # Конфигурация
├── requirements.txt     # Зависимости
├── README.md           # Документация
├── src/
│   ├── downloader.py      # Загрузка с Twitch
│   ├── audio_analyzer.py  # Анализ аудио
│   ├── chat_analyzer.py   # Анализ чата
│   ├── emotion_detector.py # Детекция эмоций
│   ├── clip_generator.py  # Создание клипов
│   ├── subtitle_gen.py    # Субтитры
│   └── utils.py           # Утилиты
├── models/              # ML модели (автозагрузка)
└── output/              # Готовые клипы
```

## 🔧 Troubleshooting

### Ошибка: "yt-dlp не найден"
```bash
pip install yt-dlp
```

### Ошибка: "whisper не установлен"
```bash
pip install openai-whisper
```

### Ошибка: "ffmpeg не найден"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Медленная обработка
- Включите GPU в `config.yaml`: `use_gpu: true`
- Уменьшите размер модели Whisper в `subtitle_gen.py`
- Обрабатывайте меньшее количество клипов

## 📝 Примеры использования

### Создание 3 клипов по 30 секунд
```bash
python main.py --input stream.mp4 --duration 30 --max-clips 3
```

### Только анализ аудио (быстро)
```bash
python main.py --input stream.mp4 --no-chat-analysis --no-emotion-detection
```

### Горизонтальный формат для YouTube
```bash
python main.py --input stream.mp4 --output-format horizontal
```

## 🎉 Готово!

Клипы будут сохранены в папке `./output/` и готовы к загрузке в:
- TikTok
- YouTube Shorts
- Instagram Reels
- Snapchat Spotlight
