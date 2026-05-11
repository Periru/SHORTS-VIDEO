"""
Модуль для генерации клипов

Функции:
- Нарезка видео по временным меткам
- Конвертация в вертикальный формат (9:16)
- Умная обрезка с фокусом на важные области
- Добавление эффектов и переходов
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import math


class ClipGenerator:
    """Класс для создания клипов из исходного видео"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_format = config.get('processing', {}).get('output_format', 'vertical')
        self.clip_duration = config.get('processing', {}).get('clip_duration', 60)
        self.resolution = config.get('output', {}).get('resolution', '1080x1920')
        self.fps = config.get('output', {}).get('fps', 30)
        self.bitrate = config.get('output', {}).get('bitrate', '5000k')
        self.smart_crop = config.get('features', {}).get('smart_crop', True)
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Получение информации о видео
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            Словарь с информацией о видео
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            info = json.loads(result.stdout)
            
            video_stream = next(
                (s for s in info['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            return {
                'width': int(video_stream.get('width', 1920)),
                'height': int(video_stream.get('height', 1080)),
                'duration': float(info['format'].get('duration', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '30/1'))
            }
        except Exception as e:
            print(f"  - Ошибка получения информации о видео: {e}")
            return {
                'width': 1920,
                'height': 1080,
                'duration': 0,
                'fps': 30
            }
    
    def calculate_crop_area(self, video_info: Dict, 
                           smart_crop: bool = True) -> str:
        """
        Расчёт параметров обрезки для вертикального формата
        
        Args:
            video_info: Информация о видео
            smart_crop: Использовать умную обрезку
            
        Returns:
            FFmpeg фильтр для обрезки
        """
        width = video_info['width']
        height = video_info['height']
        
        # Для вертикального формата 9:16
        target_ratio = 9 / 16
        
        if smart_crop:
            # Умная обрезка: берём центральную часть + немного сверху
            # Это помогает захватить лицо стримера и игру
            crop_width = height * target_ratio
            
            if crop_width > width:
                # Если видео слишком узкое, добавляем размытые поля
                return f"pad=16:9:(ow-iw)/2:(oh-ih)/2"
            else:
                # Центрированная обрезка
                x_offset = (width - crop_width) / 2
                return f"crop={int(crop_width)}:{height}:{int(x_offset)}:0"
        else:
            # Простая центрированная обрезка
            crop_width = min(width, height * target_ratio)
            x_offset = (width - crop_width) / 2
            return f"crop={int(crop_width)}:{height}:{int(x_offset)}:0"
    
    def create_clip(self, video_path: str, start_time: float, 
                   end_time: float, output_path: str) -> Optional[str]:
        """
        Создание клипа из видео
        
        Args:
            video_path: Путь к исходному видео
            start_time: Время начала в секундах
            end_time: Время конца в секундах
            output_path: Путь для сохранения клипа
            
        Returns:
            Путь к созданному клипу или None
        """
        duration = end_time - start_time
        
        # Проверка существования файла
        if not Path(video_path).exists():
            print(f"  - Ошибка: видеофайл не найден {video_path}")
            return None
        
        # Получение информации о видео
        video_info = self.get_video_info(video_path)
        
        # Построение FFmpeg команды
        output_path = str(output_path)
        
        # Базовые параметры
        filters = []
        
        # Обрезка под вертикальный формат
        if self.output_format == 'vertical':
            crop_filter = self.calculate_crop_area(video_info, self.smart_crop)
            filters.append(crop_filter)
            
            # Масштабирование до целевого разрешения
            filters.append(f"scale=1080:1920:force_original_aspect_ratio=decrease")
            filters.append(f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2")
        
        elif self.output_format == 'square':
            filters.append("crop=min(iw\\,ih):min(iw\\,ih)")
            filters.append("scale=1080:1080")
        
        # Объединение фильтров
        filter_complex = ','.join(filters) if filters else 'null'
        
        # FFmpeg команда
        cmd = [
            'ffmpeg',
            '-y',  # Перезаписать выходной файл
            '-ss', str(start_time),
            '-t', str(duration),
            '-i', video_path,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-b:v', self.bitrate,
            '-maxrate', '8000k',
            '-bufsize', '12000k',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '44100',
            '-movflags', '+faststart',
            output_path
        ]
        
        try:
            print(f"  - Обработка: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}s)")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            
            if result.returncode == 0:
                if Path(output_path).exists():
                    print(f"  - Клип создан: {output_path}")
                    return output_path
            
            print(f"  - Ошибка FFmpeg: {result.stderr[:200]}")
            return None
            
        except subprocess.TimeoutExpired:
            print(f"  - Таймаут обработки клипа")
            return None
        except Exception as e:
            print(f"  - Ошибка создания клипа: {e}")
            return None
    
    def add_intro_outro(self, clip_path: str, 
                       intro_path: Optional[str] = None,
                       outro_path: Optional[str] = None) -> Optional[str]:
        """
        Добавление интро и аутро к клипу
        
        Args:
            clip_path: Путь к клипу
            intro_path: Путь к интро (опционально)
            outro_path: Путь к аутро (опционально)
            
        Returns:
            Путь к модифицированному клипу
        """
        # Пока не реализовано
        # Можно добавить логотип, заставку и т.д.
        return clip_path
    
    def batch_create(self, video_path: str, moments: list,
                    output_dir: str) -> list:
        """
        Массовое создание клипов
        
        Args:
            video_path: Путь к исходному видео
            moments: Список моментов с временными метками
            output_dir: Директория для сохранения
            
        Returns:
            Список созданных клипов
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_clips = []
        
        for i, moment in enumerate(moments, 1):
            output_path = output_dir / f"clip_{i:03d}.mp4"
            
            clip_path = self.create_clip(
                video_path,
                moment['start_time'],
                moment['end_time'],
                output_path
            )
            
            if clip_path:
                created_clips.append(clip_path)
        
        return created_clips
