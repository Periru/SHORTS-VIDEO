"""
Модуль для детекции эмоций через компьютерное зрение

Обнаруживает:
- Радость/смех
- Удивление
- Возбуждение
- Другие выражения лица
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path


class EmotionDetector:
    """Класс для детекции эмоций на лице стримера"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.priority_emotions = config.get('emotions', {}).get(
            'priority_emotions', ['joy', 'surprise', 'excitement']
        )
        self.confidence_threshold = config.get('emotions', {}).get(
            'confidence_threshold', 0.6
        )
        
        # Попытка загрузки модели
        self.model = None
        self.face_cascade = None
        self._load_models()
    
    def _load_models(self):
        """Загрузка моделей для детекции лиц и эмоций"""
        try:
            # Загрузка каскада Хаара для детекции лиц
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            print("  - Модель детекции лиц загружена")
        except Exception as e:
            print(f"  - Предупреждение: не удалось загрузить модель лиц: {e}")
        
        # Примечание: Для реальной детекции эмоций нужна ML модель
        # Например, FER (Facial Expression Recognition) или кастомная модель
        # Здесь используется упрощённая версия
    
    def extract_frames(self, video_path: str, 
                      frame_interval: float = 1.0) -> List[Tuple[np.ndarray, float]]:
        """
        Извлечение кадров из видео
        
        Args:
            video_path: Путь к видеофайлу
            frame_interval: Интервал между кадрами в секундах
            
        Returns:
            Список кортежей (кадр, временная метка)
        """
        frames = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"  - Ошибка: не удалось открыть видео {video_path}")
            return frames
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip = int(fps * frame_interval)
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                timestamp = frame_idx / fps
                frames.append((frame, timestamp))
            
            frame_idx += 1
            
            # Прогресс
            if frame_idx % 500 == 0:
                progress = (frame_idx / total_frames) * 100
                print(f"    Обработано {progress:.1f}% кадров...")
        
        cap.release()
        print(f"  - Извлечено {len(frames)} кадров")
        return frames
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Детекция лиц в кадре
        
        Args:
            frame: Кадр изображения
            
        Returns:
            Список обнаруженных лиц с координатами
        """
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        detected = []
        for (x, y, w, h) in faces:
            detected.append({
                'bbox': (x, y, w, h),
                'confidence': 1.0  # Cascade не возвращает confidence
            })
        
        return detected
    
    def analyze_emotion_simple(self, frame: np.ndarray, 
                               face_bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Упрощённый анализ эмоций
        
        В реальной версии здесь должна быть нейросеть
        Для демонстрации используется эвристика по яркости и контрасту
        
        Args:
            frame: Кадр изображения
            face_bbox: Координаты лица (x, y, w, h)
            
        Returns:
            Словарь с эмоциями и их вероятностями
        """
        x, y, w, h = face_bbox
        
        # Вырезание области лица
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return {'emotions': {}, 'dominant': None}
        
        # Конвертация в оттенки серого
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Простые эвристики (для реальной системы нужна ML модель)
        mean_brightness = np.mean(gray_face)
        std_brightness = np.std(gray_face)
        
        # Нормализация
        brightness_score = mean_brightness / 255.0
        contrast_score = std_brightness / 128.0
        
        # Эвристика для "радости" (яркое изображение = улыбка)
        joy_score = min(1.0, brightness_score * 1.2)
        
        # Эвристика для "удивления" (высокий контраст)
        surprise_score = min(1.0, contrast_score)
        
        emotions = {
            'joy': joy_score,
            'surprise': surprise_score,
            'neutral': 1.0 - (joy_score + surprise_score) / 2
        }
        
        dominant = max(emotions.items(), key=lambda x: x[1])
        
        return {
            'emotions': emotions,
            'dominant': dominant[0] if dominant[1] > self.confidence_threshold else None
        }
    
    def detect_emotion_peaks(self, emotion_timeline: List[Dict],
                            window_size: int = 3) -> List[Dict]:
        """
        Поиск пиков эмоций во временной линии
        
        Args:
            emotion_timeline: Временная линия с эмоциями
            window_size: Размер окна для сглаживания
            
        Returns:
            Список пиковых моментов
        """
        if not emotion_timeline:
            return []
        
        peaks = []
        
        for target_emotion in self.priority_emotions:
            # Извлечение временного ряда для эмоции
            values = [
                entry['emotions'].get(target_emotion, 0) 
                for entry in emotion_timeline
            ]
            
            if not values:
                continue
            
            # Поиск локальных максимумов
            for i in range(1, len(values) - 1):
                if (values[i] > values[i-1] and 
                    values[i] > values[i+1] and
                    values[i] > self.confidence_threshold):
                    
                    peaks.append({
                        'time': emotion_timeline[i]['timestamp'],
                        'score': values[i],
                        'emotion': target_emotion,
                        'type': 'emotion_peak'
                    })
        
        return peaks
    
    def cluster_moments(self, moments: List[Dict], 
                       max_gap: float = 3.0) -> List[Dict]:
        """
        Кластеризация близких эмоциональных моментов
        
        Args:
            moments: Список моментов
            max_gap: Максимальный разрыв в секундах
            
        Returns:
            Список кластеров
        """
        if not moments:
            return []
        
        moments_sorted = sorted(moments, key=lambda x: x['time'])
        
        clusters = []
        current_cluster = [moments_sorted[0]]
        
        for moment in moments_sorted[1:]:
            if moment['time'] - current_cluster[-1]['time'] <= max_gap:
                current_cluster.append(moment)
            else:
                avg_time = sum(m['time'] for m in current_cluster) / len(current_cluster)
                max_score = max(m['score'] for m in current_cluster)
                emotions = list(set(m.get('emotion', 'unknown') for m in current_cluster))
                
                clusters.append({
                    'time': avg_time,
                    'score': max_score,
                    'emotions': emotions,
                    'moment_count': len(current_cluster)
                })
                current_cluster = [moment]
        
        if current_cluster:
            avg_time = sum(m['time'] for m in current_cluster) / len(current_cluster)
            max_score = max(m['score'] for m in current_cluster)
            emotions = list(set(m.get('emotion', 'unknown') for m in current_cluster))
            
            clusters.append({
                'time': avg_time,
                'score': max_score,
                'emotions': emotions,
                'moment_count': len(current_cluster)
            })
        
        return clusters
    
    def analyze(self, video_path: str) -> List[Dict]:
        """
        Полный анализ эмоций в видео
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            Список интересных эмоциональных моментов
        """
        print("  - Извлечение кадров...")
        frames = self.extract_frames(video_path, frame_interval=1.0)
        
        if not frames:
            return []
        
        print("  - Анализ эмоций...")
        emotion_timeline = []
        
        for frame, timestamp in frames:
            faces = self.detect_faces(frame)
            
            if faces:
                # Анализируем первое (наибольшее) лицо
                largest_face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
                emotion_result = self.analyze_emotion_simple(frame, largest_face['bbox'])
                
                emotion_timeline.append({
                    'timestamp': timestamp,
                    'emotions': emotion_result['emotions'],
                    'dominant': emotion_result['dominant'],
                    'face_detected': True
                })
            else:
                emotion_timeline.append({
                    'timestamp': timestamp,
                    'emotions': {'neutral': 1.0},
                    'dominant': None,
                    'face_detected': False
                })
        
        # Поиск пиков эмоций
        print("  - Поиск эмоциональных пиков...")
        peaks = self.detect_emotion_peaks(emotion_timeline)
        
        # Кластеризация
        print("  - Кластеризация моментов...")
        clustered = self.cluster_moments(peaks)
        
        # Преобразование в формат с start/end
        result = []
        clip_duration = self.config.get('processing', {}).get('clip_duration', 60)
        half_duration = clip_duration / 2
        
        for moment in clustered:
            start_time = max(0, moment['time'] - half_duration)
            end_time = moment['time'] + half_duration
            
            result.append({
                'start_time': start_time,
                'end_time': end_time,
                'center_time': moment['time'],
                'score': moment['score'],
                'source': 'emotion',
                'emotions': moment.get('emotions', []),
                'moment_count': moment.get('moment_count', 1)
            })
        
        return result
