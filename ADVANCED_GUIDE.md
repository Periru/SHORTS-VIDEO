# Улучшение детекции вирусного контента

Это руководство поможет настроить программу для более точного выявления потенциально вирусных фрагментов.

## 🎯 Ключевые метрики виральности

### 1. Аудио-паттерны

Вирусные клипы часто содержат:
- **Внезапные пики громкости** (крики, восклицания)
- **Смех** (особенно групповой или истерический)
- **Музыкальные моменты** (танцы, пение)
- **Звуковые эффекты** (из игр, мемов)

**Настройка в `config.yaml`:**
```yaml
audio:
  peak_threshold: 0.75  # Уменьшите для большей чувствительности
  laugh_detection: true
  scream_detection: true
```

### 2. Паттерны чата

Признаки хайповых моментов:
- **Всплеск сообщений** (>100 сообщений за 5 секунд)
- **Повторяющиеся эмодзи** (PogChamp, OMEGALUL, monkaS)
- **Мемные фразы** (POGGERS, LETSGO, INSANE)
- **Капс лок** (много сообщений CAPSLOCK)

**Настройка:**
```yaml
chat:
  hype_multiplier: 2.0  # Увеличьте вес эмодзи
  emote_priority: 
    - "PogChamp"
    - "OMEGALUL"
    - "monkaS"
    - "LUL"
    - "PepeLaugh"
```

### 3. Визуальные паттерны

Эмоциональные реакции:
- **Радость/смех** (улыбки, смех)
- **Удивление** (открытый рот, широкие глаза)
- **Шок** (резкие движения)

**Настройка:**
```yaml
emotions:
  priority_emotions:
    - "joy"
    - "surprise"
    - "excitement"
  confidence_threshold: 0.5  # Уменьшите для большей чувствительности
```

## 🔬 Продвинутые техники

### Добавление кастомных детекторов

#### 1. Детекция игровых моментов

Создайте файл `src/game_event_detector.py`:

```python
"""Детектор важных игровых событий"""

class GameEventDetector:
    def __init__(self, config):
        self.config = config
        # Ключевые слова для разных игр
        self.game_keywords = {
            'valorant': ['ACE', 'CLUTCH', 'PLANT', 'DEFUSE'],
            'league': ['PENTAKILL', 'BARON', 'DRAGON'],
            'cs-go': ['ACE', 'CLUTCH', 'DEFUSE'],
        }
    
    def detect(self, chat_data, game='general'):
        # Логика детекции
        pass
```

#### 2. Детекция коллабораций

Когда на стриме несколько человек:
- Добавьте детекцию нескольких лиц
- Отслеживайте упоминания гостей в чате
- Анализируйте изменения в тоне разговора

#### 3. ML-модель для классификации

Для максимальной точности можно обучить модель:

```python
from transformers import AutoModelForSequenceClassification

# Загрузка предобученной модели для классификации текста
model = AutoModelForSequenceClassification.from_pretrained(
    "finiteautomata/bertweet-base-sentiment-analysis"
)

# Классификация сообщений чата
def classify_chat_sentiment(messages):
    # Анализ тональности
    pass
```

### Интеграция с API соцсетей

Для анализа трендов:

```python
import requests

def get_tiktok_trends():
    """Получение трендовых звуков и хэштегов"""
    # Интеграция с TikTok API
    pass

def get_youtube_shorts_trends():
    """Получение трендов YouTube Shorts"""
    # Интеграция с YouTube API
    pass
```

## 📊 Оптимизация скоринга

### Формула комплексного скоринга

В файле `src/utils.py` функция `calculate_moment_score`:

```python
def calculate_moment_score(moment, weights=None):
    if weights is None:
        weights = {
            'audio': 0.4,      # 40% аудио
            'chat': 0.35,      # 35% чат
            'emotion': 0.25    # 25% эмоции
        }
    
    # Базовый скор
    base_score = moment.get('score', 0.5)
    
    # Бонусы
    count_bonus = min(0.2, moment_count * 0.05)
    type_bonus = calculate_type_bonus(moment)
    
    # Множитель для комбо-детекций
    combo_multiplier = 1.0
    if len(moment.get('sources', [])) > 1:
        combo_multiplier = 1.2  # +20% если детектировано несколькими методами
    
    final_score = (base_score + count_bonus + type_bonus) * combo_multiplier
    return min(1.0, final_score)
```

### A/B тестирование параметров

1. Создайте несколько конфигураций:
   - `config_aggressive.yaml` (низкие пороги, много клипов)
   - `config_conservative.yaml` (высокие пороги, только топ)
   - `config_balanced.yaml` (средние значения)

2. Протестируйте на известных вирусных клипах

3. Сравните результаты и выберите оптимальные параметры

## 🎬 Пост-обработка для виральности

### 1. Динамические субтитры

Добавьте анимированные субтитры:

```python
# В subtitle_gen.py добавьте стили
animated_style = (
    "PrimaryColour=&H00FFFF&,SecondaryColour=&H0000FF&,"
    "OutlineColour=&H000000&,BackColour=&H80000000&,"
    "Bold=-1,Italic=0,Underline=0,StrikeOut=0,"
    "ScaleX=100,ScaleY=100,Spacing=0,Angle=0,"
    "BorderStyle=4,Effect=typewriter"
)
```

### 2. Автоматическое добавление эффектов

- **Zoom-in** на эмоциональных моментах
- **Тряска камеры** при криках
- **Эмодзи оверлей** при детекции мемов

### 3. Оптимизация под платформы

```yaml
output:
  tiktok:
    resolution: "1080x1920"
    max_duration: 60
    hashtags: ["#fyp", "#viral", "#gaming"]
  
  youtube_shorts:
    resolution: "1080x1920"
    max_duration: 60
  
  instagram_reels:
    resolution: "1080x1920"
    max_duration: 90
```

## 📈 Аналитика и улучшение

### Сбор статистики

Добавьте логирование:

```python
import json
from datetime import datetime

def log_clip_metrics(clip_data):
    """Логирование метрик для анализа"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'clip_score': clip_data['score'],
        'audio_peaks': clip_data['audio_count'],
        'chat_spikes': clip_data['chat_count'],
        'emotions': clip_data['emotions'],
        'duration': clip_data['duration']
    }
    
    with open('clip_analytics.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Обратная связь

1. Загрузите клипы в соцсети
2. Соберите статистику (просмотры, лайки, шеры)
3. Коррелируйте с внутренними скорами
4. Настройте веса в формуле скоринга

### Continuous Learning

```python
# Псевдокод для системы обучения
def update_weights_from_performance(historical_clips):
    """Обновление весов на основе исторических данных"""
    
    viral_clips = [c for c in historical_clips if c['views'] > 100000]
    
    # Анализ общих паттернов вирусных клипов
    avg_audio_score = mean(c['audio_score'] for c in viral_clips)
    avg_chat_score = mean(c['chat_score'] for c in viral_clips)
    avg_emotion_score = mean(c['emotion_score'] for c in viral_clips)
    
    # Корректировка весов
    new_weights = {
        'audio': normalize(avg_audio_score),
        'chat': normalize(avg_chat_score),
        'emotion': normalize(avg_emotion_score)
    }
    
    return new_weights
```

## 🚀 Чеклист перед запуском

- [ ] Настроены пороги детекции под ваш контент
- [ ] Добавлены приоритетные эмодзи для вашей аудитории
- [ ] Протестировано на известном вирусном клипе
- [ ] Настроено качество выходного видео
- [ ] Проверена работа всех модулей
- [ ] Есть план сбора обратной связи

## 📚 Дополнительные ресурсы

- [Twitch API Documentation](https://dev.twitch.tv/docs/api)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [FFmpeg Filters](https://ffmpeg.org/ffmpeg-filters.html)
- [TikTok for Developers](https://developers.tiktok.com/)

---

**Совет:** Начните с консервативных настроек и постепенно увеличивайте чувствительность, анализируя результаты!
