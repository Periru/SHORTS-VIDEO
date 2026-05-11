"""
Модуль для генерации субтитров

Использует Whisper для транскрибации аудио
и добавления стилизованных субтитров к видео
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import json


class SubtitleGenerator:
    """Класс для генерации и добавления субтитров"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.font = config.get('subtitles', {}).get('font', 'Arial')
        self.font_size = config.get('subtitles', {}).get('font_size', 48)
        self.color = config.get('subtitles', {}).get('color', 'white')
        self.outline_color = config.get('subtitles', {}).get('outline_color', 'black')
        self.position = config.get('subtitles', {}).get('position', 'bottom')
        
        # Модель Whisper
        self.whisper_model = None
        self._load_whisper()
    
    def _load_whisper(self):
        """Загрузка модели Whisper"""
        try:
            import whisper
            model_size = "base"  # Можно изменить на "small", "medium", "large"
            self.whisper_model = whisper.load_model(model_size)
            print("  - Модель Whisper загружена")
        except ImportError:
            print("  - Предупреждение: whisper не установлен")
            print("    Установите: pip install openai-whisper")
        except Exception as e:
            print(f"  - Предупреждение: ошибка загрузки Whisper: {e}")
    
    def transcribe(self, audio_path: str, language: str = "ru") -> List[Dict]:
        """
        Транскрибация аудио в текст с временными метками
        
        Args:
            audio_path: Путь к аудиофайлу
            language: Язык аудио
            
        Returns:
            Список сегментов с текстом и временем
        """
        if self.whisper_model is None:
            print("  - Whisper недоступен, пропускаем транскрибацию")
            return []
        
        try:
            print("  - Транскрибация аудио...")
            
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True
            )
            
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            print(f"  - Найдено {len(segments)} сегментов")
            return segments
            
        except Exception as e:
            print(f"  - Ошибка транскрибации: {e}")
            return []
    
    def create_srt_file(self, segments: List[Dict], output_path: str) -> str:
        """
        Создание SRT файла субтитров
        
        Args:
            segments: Список сегментов
            output_path: Путь для сохранения SRT
            
        Returns:
            Путь к созданному файлу
        """
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{format_time(segment['start'])} --> {format_time(segment['end'])}\n")
                f.write(f"{segment['text']}\n\n")
        
        return output_path
    
    def add_subtitles_to_video(self, video_path: str, 
                               srt_path: str, 
                               output_path: str) -> Optional[str]:
        """
        Добавление субтитров к видео через FFmpeg
        
        Args:
            video_path: Путь к видео
            srt_path: Путь к SRT файлу
            output_path: Путь для выходного видео
            
        Returns:
            Путь к видео с субтитрами или None
        """
        # Построение фильтра для субтитров
        # Для вертикального видео нужно учесть масштабирование
        
        font_config = f"FontName={self.font},FontSize={self.font_size}," \
                     f"PrimaryColour=&H{self.color}&,OutlineColour=&H{self.outline_color}&," \
                     f"Outline=2,BorderStyle=4"
        
        # Позиционирование (для вертикального видео)
        if self.position == 'bottom':
            margin_v = 50
        elif self.position == 'top':
            margin_v = 1870  # Для 1920p
        else:
            margin_v = 960  # Центр
        
        filter_complex = (
            f"subtitles={srt_path}:force_style='{font_config},"
            f"MarginV={margin_v},Alignment=2'"
        )
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vf', filter_complex,
            '-c:a', 'copy',
            output_path
        ]
        
        try:
            print(f"  - Добавление субтитров...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                if Path(output_path).exists():
                    print(f"  - Субтитры добавлены: {output_path}")
                    return output_path
            
            print(f"  - Ошибка FFmpeg: {result.stderr[:200]}")
            return None
            
        except subprocess.TimeoutExpired:
            print(f"  - Таймаут обработки субтитров")
            return None
        except Exception as e:
            print(f"  - Ошибка добавления субтитров: {e}")
            return None
    
    def extract_audio(self, video_path: str, temp_dir: str = "./temp") -> str:
        """
        Извлечение аудио из видео
        
        Args:
            video_path: Путь к видео
            temp_dir: Временная директория
            
        Returns:
            Путь к аудиофайлу
        """
        temp_path = Path(temp_dir)
        temp_path.mkdir(parents=True, exist_ok=True)
        
        audio_path = temp_path / "temp_audio.wav"
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return str(audio_path)
        except Exception as e:
            print(f"  - Ошибка извлечения аудио: {e}")
            return ""
    
    def add_subtitles(self, clip_path: str) -> Optional[str]:
        """
        Полный процесс добавления субтитров к клипу
        
        Args:
            clip_path: Путь к клипу
            
        Returns:
            Путь к клипу с субтитрами или None
        """
        from tempfile import mkdtemp
        
        temp_dir = mkdtemp()
        clip_path_obj = Path(clip_path)
        
        # Извлечение аудио
        audio_path = self.extract_audio(clip_path, temp_dir)
        
        if not audio_path or not Path(audio_path).exists():
            print("  - Не удалось извлечь аудио")
            return clip_path
        
        # Транскрибация
        segments = self.transcribe(audio_path)
        
        if not segments:
            print("  - Не удалось получить субтитры")
            return clip_path
        
        # Создание SRT
        srt_path = Path(temp_dir) / "subtitles.srt"
        self.create_srt_file(segments, str(srt_path))
        
        # Добавление к видео
        output_path = clip_path_obj.parent / f"{clip_path_obj.stem}_subtitled.mp4"
        
        subtitled_path = self.add_subtitles_to_video(
            clip_path,
            str(srt_path),
            str(output_path)
        )
        
        # Очистка временных файлов
        try:
            Path(audio_path).unlink()
            srt_path.unlink()
        except:
            pass
        
        return subtitled_path if subtitled_path else clip_path
    
    def generate_highlighted_subtitles(self, segments: List[Dict],
                                       keywords: List[str] = None) -> List[Dict]:
        """
        Генерация субтитров с подсветкой ключевых слов
        
        Args:
            segments: Список сегментов
            keywords: Ключевые слова для подсветки
            
        Returns:
            Модифицированные сегменты
        """
        if keywords is None:
            keywords = ['OMG', 'WOW', 'POG', 'LETSGO', 'INSANE', 'CLUTCH']
        
        highlighted = []
        
        for segment in segments:
            text = segment['text']
            
            # Подсветка ключевых слов (для ASS формата)
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    # Замена на форматированный текст
                    text = text.replace(
                        keyword,
                        f"{{\\c&H00FFFF&}}{keyword}{{\\c&HFFFFFF&}}"
                    )
            
            highlighted.append({
                **segment,
                'text': text
            })
        
        return highlighted
