"""
Twitch Clip Generator - Main Entry Point

Автоматическое создание вирусных клипов из Twitch трансляций
для TikTok и YouTube Shorts
"""

import argparse
import yaml
import os
from pathlib import Path
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

def load_config(config_path="config.yaml"):
    """Загрузка конфигурации из YAML файла"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(
        description="Twitch Clip Generator - Автоматическое создание вирусных клипов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py --channel "shroud" --video_id "1234567890"
  python main.py --input "path/to/video.mp4"
  python main.py --channel "ninja" --duration 60 --max-clips 3
        """
    )
    
    parser.add_argument(
        "--channel",
        type=str,
        help="Имя Twitch канала"
    )
    
    parser.add_argument(
        "--video_id",
        type=str,
        help="ID видео (VOD) с Twitch"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        help="Путь к локальному видеофайлу"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Длительность клипа в секундах (по умолчанию: 60)"
    )
    
    parser.add_argument(
        "--max-clips",
        type=int,
        default=5,
        help="Максимальное количество клипов (по умолчанию: 5)"
    )
    
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["vertical", "square", "horizontal"],
        default="vertical",
        help="Формат выходного видео (по умолчанию: vertical)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Путь к файлу конфигурации"
    )
    
    parser.add_argument(
        "--no-audio-analysis",
        action="store_true",
        help="Отключить анализ аудио"
    )
    
    parser.add_argument(
        "--no-chat-analysis",
        action="store_true",
        help="Отключить анализ чата"
    )
    
    parser.add_argument(
        "--no-emotion-detection",
        action="store_true",
        help="Отключить детекцию эмоций"
    )
    
    parser.add_argument(
        "--no-subtitles",
        action="store_true",
        help="Отключить генерацию субтитров"
    )
    
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Использовать GPU для ускорения"
    )
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "🎬 Twitch Clip Generator")
    print(Fore.CYAN + "=" * 60)
    
    config = load_config(args.config)
    
    # Переопределение конфига аргументами командной строки
    if args.duration:
        config['processing']['clip_duration'] = args.duration
    if args.max_clips:
        config['processing']['max_clips'] = args.max_clips
    if args.output_format:
        config['processing']['output_format'] = args.output_format
    if args.no_audio_analysis:
        config['features']['analyze_audio'] = False
    if args.no_chat_analysis:
        config['features']['analyze_chat'] = False
    if args.no_emotion_detection:
        config['features']['detect_emotions'] = False
    if args.no_subtitles:
        config['features']['generate_subtitles'] = False
    if args.gpu:
        config['performance']['use_gpu'] = True
    
    # Проверка входных данных
    if not args.channel and not args.input:
        print(Fore.RED + "\n❌ Ошибка: Укажите --channel или --input")
        parser.print_help()
        return 1
    
    # Создание директорий
    output_dir = Path(config['output']['directory'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(Fore.GREEN + f"\n✅ Конфигурация загружена")
    print(Fore.YELLOW + f"📁 Выходная директория: {output_dir.absolute()}")
    print(Fore.YELLOW + f"⏱️  Длительность клипа: {config['processing']['clip_duration']} сек")
    print(Fore.YELLOW + f"🎯 Максимум клипов: {config['processing']['max_clips']}")
    
    # Импорт модулей обработки
    try:
        from src.downloader import TwitchDownloader
        from src.audio_analyzer import AudioAnalyzer
        from src.chat_analyzer import ChatAnalyzer
        from src.emotion_detector import EmotionDetector
        from src.clip_generator import ClipGenerator
        from src.subtitle_gen import SubtitleGenerator
        
        print(Fore.GREEN + "\n✅ Все модули успешно импортированы")
    except ImportError as e:
        print(Fore.RED + f"\n❌ Ошибка импорта модулей: {e}")
        print(Fore.YELLOW + "\nУбедитесь, что все зависимости установлены:")
        print(Fore.WHITE + "pip install -r requirements.txt")
        return 1
    
    # Основной пайплайн обработки
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + "🚀 Запуск обработки...")
    print(Fore.CYAN + "=" * 60)
    
    video_path = None
    
    # Шаг 1: Загрузка видео
    if args.input:
        print(Fore.BLUE + f"\n📥 Использование локального файла: {args.input}")
        video_path = args.input
    elif args.channel:
        print(Fore.BLUE + f"\n📥 Загрузка VOD с канала: {args.channel}")
        if args.video_id:
            downloader = TwitchDownloader(config)
            video_path = downloader.download_vod(args.channel, args.video_id)
        else:
            downloader = TwitchDownloader(config)
            video_path = downloader.download_latest_vod(args.channel)
    
    if not video_path or not os.path.exists(video_path):
        print(Fore.RED + "\n❌ Ошибка: Видеофайл не найден")
        return 1
    
    print(Fore.GREEN + f"\n✅ Видео загружено: {video_path}")
    
    # Шаг 2: Анализ аудио
    interesting_moments = []
    
    if config['features']['analyze_audio']:
        print(Fore.BLUE + "\n🔊 Анализ аудио...")
        audio_analyzer = AudioAnalyzer(config)
        audio_peaks = audio_analyzer.analyze(video_path)
        interesting_moments.extend(audio_peaks)
        print(Fore.GREEN + f"✅ Найдено {len(audio_peaks)} аудио-пиков")
    
    # Шаг 3: Анализ чата
    if config['features']['analyze_chat'] and args.channel:
        print(Fore.BLUE + "\n💬 Анализ активности чата...")
        chat_analyzer = ChatAnalyzer(config)
        chat_highlights = chat_analyzer.analyze(args.channel, args.video_id)
        interesting_moments.extend(chat_highlights)
        print(Fore.GREEN + f"✅ Найдено {len(chat_highlights)} хайповых моментов в чате")
    
    # Шаг 4: Детекция эмоций
    if config['features']['detect_emotions']:
        print(Fore.BLUE + "\n😐 Детекция эмоций...")
        emotion_detector = EmotionDetector(config)
        emotion_highlights = emotion_detector.analyze(video_path)
        interesting_moments.extend(emotion_highlights)
        print(Fore.GREEN + f"✅ Найдено {len(emotion_highlights)} эмоциональных моментов")
    
    # Шаг 5: Композитный скоринг и выбор лучших моментов
    print(Fore.BLUE + "\n🎯 Вычисление лучших моментов...")
    from src.utils import score_and_select_moments
    
    selected_moments = score_and_select_moments(
        interesting_moments,
        config['processing']['clip_duration'],
        config['processing']['max_clips'],
        config['processing']['min_clip_score']
    )
    
    print(Fore.GREEN + f"✅ Выбрано {len(selected_moments)} лучших моментов")
    
    # Шаг 6: Генерация клипов
    print(Fore.BLUE + "\n✂️  Нарезка клипов...")
    clip_generator = ClipGenerator(config)
    
    generated_clips = []
    for i, moment in enumerate(selected_moments, 1):
        print(Fore.YELLOW + f"\n📹 Обработка клипа {i}/{len(selected_moments)}")
        clip_path = clip_generator.create_clip(
            video_path,
            moment['start_time'],
            moment['end_time'],
            output_dir / f"clip_{i:03d}.mp4"
        )
        if clip_path:
            generated_clips.append(clip_path)
            print(Fore.GREEN + f"✅ Клип создан: {clip_path}")
    
    # Шаг 7: Генерация субтитров
    if config['features']['generate_subtitles'] and generated_clips:
        print(Fore.BLUE + "\n📝 Генерация субтитров...")
        subtitle_gen = SubtitleGenerator(config)
        
        for clip_path in generated_clips:
            print(Fore.YELLOW + f"\n📝 Обработка: {clip_path}")
            subtitled_path = subtitle_gen.add_subtitles(clip_path)
            if subtitled_path:
                print(Fore.GREEN + f"✅ Субтитры добавлены: {subtitled_path}")
    
    # Финальный отчет
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.GREEN + "✨ Обработка завершена!")
    print(Fore.CYAN + "=" * 60)
    print(Fore.WHITE + f"\n📁 Создано клипов: {len(generated_clips)}")
    print(Fore.WHITE + f"📂 Директория: {output_dir.absolute()}")
    
    if generated_clips:
        print(Fore.GREEN + "\n📋 Список файлов:")
        for clip in generated_clips:
            print(Fore.WHITE + f"   - {clip}")
    
    print(Fore.CYAN + "\n🎉 Готово к загрузке в TikTok и YouTube Shorts!")
    print(Fore.CYAN + "=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
