# Twitch Clip Generator - Автоматическое создание вирусных клипов

Программа для автоматического выделения мемных фрагментов из Twitch-трансляций и создания вертикальных клипов для TikTok и YouTube Shorts.

## Возможности

- 🎬 Автоматическая загрузка VOD с Twitch
- 🔊 Анализ аудио на пиковые моменты (смех, крики, реакции)
- 💬 Анализ активности чата для выявления хайповых моментов
- 😐 Детекция эмоций через компьютерное зрение
- 📱 Автоматическая нарезка в формат 9:16 (вертикальное видео)
- 📝 Автогенерация субтитров
- ⚡ Пакетная обработка

## Установка

### Требования
- Python 3.9+
- FFmpeg (обязательно!)
- CUDA GPU (опционально, для ускорения ML-моделей)

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
pip install -r requirements.txt
```

### Шаг 3: Настройка

Отредактируйте `config.yaml` и укажите:
- Ваш Twitch канал
- Параметры обработки
- Пути для сохранения

## Использование

### Базовое использование

```bash
python main.py --channel "shroud" --video_id "1234567890"
```

### Обработка локального файла

```bash
python main.py --input "path/to/video.mp4"
```

### С кастомными настройками

```bash
python main.py --channel "ninja" --duration 60 --output-format "tiktok"
```

## Структура проекта

```
twitch-clip-generator/
├── main.py                 # Точка входа
├── config.yaml            # Конфигурация
├── requirements.txt       # Зависимости
├── src/
│   ├── downloader.py      # Загрузка видео с Twitch
│   ├── audio_analyzer.py  # Анализ аудио-пиков
│   ├── chat_analyzer.py   # Анализ активности чата
│   ├── emotion_detector.py # Детекция эмоций
│   ├── clip_generator.py  # Создание клипов
│   ├── subtitle_gen.py    # Генерация субтитров
│   └── utils.py           # Утилиты
├── models/                # ML модели
└── output/                # Готовые клипы
```

## Алгоритм работы

1. **Загрузка**: Скачиваем VOD и данные чата через Twitch API
2. **Анализ аудио**: Ищем пики громкости, смех, восклицания
3. **Анализ чата**: Находим всплески активности (Kappa, PogChamp и т.д.)
4. **Композитный скоринг**: Объединяем метрики для выявления лучших моментов
5. **Нарезка**: Вырезаем клипы 30-60 секунд в формате 9:16
6. **Пост-обработка**: Добавляем субтитры, эмодзи, эффекты

## Конфигурация

Пример `config.yaml`:

```yaml
twitch:
  client_id: "your_client_id"
  oauth_token: "your_oauth_token"

processing:
  clip_duration: 60  # секунд
  min_clip_score: 0.7  # порог качества
  output_format: "vertical"  # vertical, square, horizontal
  
features:
  analyze_audio: true
  analyze_chat: true
  detect_emotions: true
  generate_subtitles: true

output:
  directory: "./output"
  format: "mp4"
  resolution: "1080x1920"
```

## Лицензия

MIT License