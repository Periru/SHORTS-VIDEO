# Twitch Clip Generator - Автоматическое создание вирусных клипов

## 🚀 Быстрая установка на ПК

### Шаг 1: Установка Python (если не установлен)

**Windows:**
1. Скачайте Python 3.9+ с [python.org](https://www.python.org/downloads/)
2. При установке **ОБЯЗАТЕЛЬНО** отметьте галочку "Add Python to PATH"
3. Нажмите "Install Now"

**macOS:**
```bash
brew install python@3.9
```
Или скачайте с [python.org](https://www.python.org/downloads/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.9 python3-pip python3-venv ffmpeg
```

### Шаг 2: Установка FFmpeg (обязательно для обработки видео)

**Windows:**
1. Скачайте с [ffmpeg.org](https://ffmpeg.org/download.html) (выберите Windows)
2. Распакуйте в `C:\ffmpeg`
3. Добавьте в PATH:
   - Правый клик на "Этот компьютер" → Свойства
   - Дополнительные параметры системы → Переменные среды
   - В "System variables" найдите `Path` → Изменить
   - Добавить `C:\ffmpeg\bin`
4. Перезапустите терминал

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Шаг 3: Клонирование проекта

Откройте терминал (Command Prompt, PowerShell или Terminal):

```bash
cd %USERPROFILE%  # Windows
# или
cd ~  # macOS/Linux

git clone https://github.com/yourusername/twitch-clip-generator.git
cd twitch-clip-generator
```

Или если у вас уже есть файлы в папке:
```bash
cd путь/к/проекту/twitch-clip-generator
```

### Шаг 4: Создание виртуального окружения (рекомендуется)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Шаг 5: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 6: Проверка установки

```bash
python main.py --help
```

Если видите справку - всё установлено правильно! ✅

---

## 🎯 Первое использование

### Базовый пример:
```bash
python main.py --input "stream.mp4" --duration 60 --max-clips 5
```

### Скачать с Twitch и создать клипы:
```bash
python main.py --twitch-url "https://twitch.tv/videos/123456789" --duration 60 --max-clips 5
```

### С продвинутыми настройками:
```bash
python main.py --input "stream.mp4" --duration 90 --max-clips 10 --sensitivity high --output-format mp4
```

---

## ⚙️ Настройка конфигурации

Откройте `config.yaml` и настройте под себя:

```yaml
# Минимальная длительность клипа (сек)
min_clip_duration: 30

# Максимальная длительность (сек)
max_clip_duration: 90

# Чувствительность детекции (low, medium, high)
detection_sensitivity: medium

# Формат вывода
output_format: mp4

# Качество видео
video_quality: high

# Автоматически добавлять субтитры
auto_captions: true

# Язык для субтитров
caption_language: ru

# Платформа оптимизации (tiktok, youtube_shorts, instagram_reels)
platform: tiktok
```

---

## 📁 Структура проекта

```
twitch-clip-generator/
├── main.py              # Главный скрипт
├── config.yaml          # Конфигурация
├── requirements.txt     # Зависимости
├── src/
│   ├── __init__.py
│   ├── downloader.py    # Загрузка с Twitch
│   ├── detector.py      # Детекция вирусных моментов
│   ├── audio_analyzer.py # Анализ аудио
│   ├── chat_analyzer.py # Анализ чата
│   ├── editor.py        # Монтаж клипов
│   ├── captioner.py     # Субтитры
│   └── utils.py         # Утилиты
├── output/              # Готовые клипы
└── logs/                # Логи работы
```

---

## 🔧 Решение проблем

### Ошибка: "ffmpeg not found"
- Убедитесь, что FFmpeg установлен и добавлен в PATH
- Перезапустите терминал после установки

### Ошибка: "ModuleNotFoundError"
```bash
pip install -r requirements.txt --upgrade
```

### Ошибка: "No module named 'src'"
Запускайте из корневой папки проекта:
```bash
cd twitch-clip-generator
python main.py ...
```

### Медленная обработка
- Уменьшите `max-clips` в настройках
- Используйте SSD диск
- Закройте другие программы

---

## 🎓 Примеры использования

### 1. Создать 3 клипа по 60 секунд из видео:
```bash
python main.py --input "my_stream.mp4" --duration 60 --max-clips 3
```

### 2. Обработать с высокой чувствительностью:
```bash
python main.py --input "stream.mp4" --sensitivity high --max-clips 5
```

### 3. Только для YouTube Shorts:
```bash
python main.py --input "stream.mp4" --platform youtube_shorts --duration 90
```

### 4. Пакетная обработка нескольких файлов:
```bash
python main.py --input-folder "./streams" --duration 60 --max-clips 3
```

---

## 📊 Как это работает

1. **Загрузка** - Скачивает видео с Twitch или использует локальный файл
2. **Анализ аудио** - Ищет пики громкости, смех, эмоциональные моменты
3. **Анализ чата** - Определяет всплески активности, хайповые эмодзи
4. **Детекция эмоций** - Использует AI для распознавания эмоций
5. **Скоринг** - Присваивает каждому фрагменту рейтинг "вирусности"
6. **Монтаж** - Вырезает лучшие моменты, кадрирует в 9:16
7. **Субтитры** - Автоматически генерирует текст (опционально)
8. **Экспорт** - Сохраняет готовые клипы в `./output/`

---

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи в папке `logs/`
2. Убедитесь, что все зависимости установлены
3. Обновите пакеты: `pip install -r requirements.txt --upgrade`

---

## 📝 Лицензия

MIT License - используйте свободно!
