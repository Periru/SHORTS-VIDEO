# 🎬 Twitch Clip Generator Pro

**Автоматическое создание вирусных клипов из Twitch-трансляций для TikTok и YouTube Shorts**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## ✨ Возможности

- 🤖 **AI-детекция вирусного контента** - автоматический поиск мемных моментов
- 📊 **Анализ аудио** - обнаружение смеха, криков, эмоциональных пиков
- 💬 **Анализ чата** - отслеживание всплесков активности в Twitch-чате
- 🎥 **Авто-кадрирование** - конвертация в вертикальный формат 9:16
- 📝 **Субтитры** - автоматическая генерация субтитров через Whisper AI
- 🔄 **Мультиформатность** - экспорт в MP4, MOV, WebM, GIF
- 🎨 **Современный GUI** - удобный интерфейс на CustomTkinter

## 🚀 Быстрый старт

### Шаг 1: Установка Python
Скачайте и установите Python 3.8+ с [python.org](https://www.python.org/downloads/)

**Важно:** При установке поставьте галочку ✅ "Add Python to PATH"

### Шаг 2: Установка FFmpeg

#### Windows:
1. Скачайте сборку с [ffmpeg.org](https://ffmpeg.org/download.html)
2. Распакуйте в `C:\ffmpeg`
3. Добавьте `C:\ffmpeg\bin` в системную переменную PATH
4. Перезапустите терминал

#### macOS:
```bash
brew install ffmpeg
```

#### Linux:
```bash
sudo apt update && sudo apt install ffmpeg
```

### Шаг 3: Установка приложения

```bash
# Перейдите в папку проекта
cd twitch_clip_app

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 4: Запуск приложения

```bash
python src/gui.py
```

Или создайте ярлык для удобного запуска (см. ниже).

## 📖 Использование

### Основной рабочий процесс:

1. **Загрузите видео**
   - Нажмите "Загрузить видео" и выберите файл
   - Или "Загрузить с Twitch" для URL трансляции

2. **Настройте параметры**
   - Длительность клипа (15-180 сек)
   - Количество клипов (1-20)
   - Чувствительность детекции
   - Опции: субтитры, кадрирование, улучшение аудио

3. **Выберите форматы экспорта**
   - MP4 (H.264) - универсальный формат
   - MP4 (HEVC) - высокое качество
   - MOV - для монтажа
   - WebM - для веба
   - GIF - анимация

4. **Запустите обработку**
   - Нажмите "🚀 Начать обработку"
   - Дождитесь завершения
   - Готовые клипы появятся в папке output/

## 🛠 Создание исполняемого файла (.exe)

Для создания standalone-приложения, которое можно установить на любой ПК:

### Установка PyInstaller:
```bash
pip install pyinstaller
```

### Сборка .exe (Windows):
```bash
pyinstaller --onefile --windowed --name "TwitchClipGenerator" --icon=assets/icon.ico src/gui.py
```

### Сборка .app (macOS):
```bash
pyinstaller --onefile --windowed --name "TwitchClipGenerator" --icon=assets/icon.icns src/gui.py
```

Готовый файл появится в папке `dist/`.

### Создание установщика (Windows):

1. Установите [Inno Setup](https://jrsoftware.org/isdl.php)
2. Используйте скрипт `installers/setup.iss` (создаётся отдельно)
3. Скомпилируйте установщик

## 📁 Структура проекта

```
twitch_clip_app/
├── src/
│   ├── gui.py              # Графический интерфейс
│   ├── video_processor.py  # Обработка видео
│   ├── clip_detector.py    # Детекция клипов
│   └── config_manager.py   # Управление настройками
├── assets/                 # Иконки, изображения
├── installers/             # Скрипты для создания установщиков
├── requirements.txt        # Зависимости Python
├── config.yaml            # Конфигурация (создаётся автоматически)
└── README.md              # Этот файл
```

## ⚙️ Конфигурация

При первом запуске создаётся файл `config.yaml` с настройками:

```yaml
processing:
  default_duration: 60      # Длительность клипа по умолчанию
  max_clips: 5              # Максимум клипов
  sensitivity: 0.6          # Чувствительность детекции
  auto_crop: true           # Авто-кадрирование 9:16
  add_subtitles: true       # Генерировать субтитры
  
output:
  directory: ./output       # Папка для сохранения
  formats: [mp4_h264]       # Форматы по умолчанию
  
ai:
  use_whisper: true         # Использовать Whisper для субтитров
  whisper_model: base       # Модель Whisper
```

## 🔧 Расширенные возможности

### Интеграция с Twitch API

Для загрузки трансляций напрямую:

1. Получите Client ID и OAuth токен на [dev.twitch.tv](https://dev.twitch.tv)
2. Добавьте их в `config.yaml`:

```yaml
twitch:
  client_id: ваш_client_id
  oauth_token: ваш_oauth_token
  download_quality: best
```

### Настройка AI-моделей

Для улучшения детекции:

```yaml
ai:
  detect_faces: true        # Детекция лиц
  detect_emotions: true     # Детекция эмоций
  whisper_model: medium     # more accurate but slower
```

## ❓ Решение проблем

### Ошибка: "ffmpeg not found"
- Убедитесь, что FFmpeg установлен и добавлен в PATH
- Проверьте: `ffmpeg -version` в терминале

### Ошибка: "No module named 'customtkinter'"
- Активируйте виртуальное окружение
- Переустановите зависимости: `pip install -r requirements.txt`

### Медленная обработка
- Уменьшите количество клипов
- Используйте меньшую длительность
- Отключите субтитры (Whisper требует ресурсов)

### Плохое качество клипов
- В настройках выберите MP4 (HEVC) для лучшего качества
- Увеличьте битрейт в config.yaml

## 📝 Лицензия

MIT License - свободное использование и модификация

## 🤝 Поддержка

Если возникли вопросы или проблемы:
1. Проверьте раздел "Решение проблем"
2. Посмотрите логи в приложении
3. Создайте issue в репозитории

---

**Создано для контент-мейкеров | Автоматизируйте создание вирусного контента** 🚀
