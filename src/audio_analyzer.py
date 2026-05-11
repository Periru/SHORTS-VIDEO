"""
Модуль для анализа аудио

Обнаруживает:
- Пики громкости
- Смех
- Крики и восклицания
- Другие звуковые события
"""

import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Any, Tuple
from pathlib import Path


class AudioAnalyzer:
    """Класс для анализа аудио дорожки видео"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.peak_threshold = config.get('audio', {}).get('peak_threshold', 0.8)
        self.laugh_detection = config.get('audio', {}).get('laugh_detection', True)
        self.scream_detection = config.get('audio', {}).get('scream_detection', True)
        
    def load_audio(self, video_path: str) -> Tuple[np.ndarray, int]:
        """
        Загрузка аудио из видеофайла
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            Кортеж (аудио данные, частота дискретизации)
        """
        try:
            # Извлечение аудио с помощью librosa
            y, sr = librosa.load(video_path, sr=None)
            return y, sr
        except Exception as e:
            print(f"Ошибка загрузки аудио: {e}")
            return np.array([]), 0
    
    def extract_features(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """
        Извлечение аудио признаков
        
        Args:
            audio: Аудио данные
            sr: Частота дискретизации
            
        Returns:
            Словарь с признаками
        """
        features = {}
        
        # RMS энергия (громкость)
        features['rms'] = librosa.feature.rms(y=audio)[0]
        
        # Zero crossing rate (для детекции смеха)
        features['zcr'] = librosa.feature.zero_crossing_rate(audio)[0]
        
        # Spectral centroid (тембр)
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        
        # MFCC (для классификации звуков)
        features['mfcc'] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        
        return features
    
    def detect_volume_peaks(self, features: Dict[str, np.ndarray], 
                           sr: int, hop_length: int = 512) -> List[Dict]:
        """
        Обнаружение пиков громкости
        
        Args:
            features: Словарь с признаками
            sr: Частота дискретизации
            hop_length: Шаг окна анализа
            
        Returns:
            Список найденных пиков
        """
        rms = features['rms']
        threshold = np.percentile(rms, 85)  # Топ 15% по громкости
        
        peaks = []
        for i in range(1, len(rms) - 1):
            if rms[i] > threshold and rms[i] > rms[i-1] and rms[i] > rms[i+1]:
                time_seconds = i * hop_length / sr
                peaks.append({
                    'time': time_seconds,
                    'score': float(rms[i] / np.max(rms)),
                    'type': 'volume_peak'
                })
        
        return peaks
    
    def detect_laughter(self, features: Dict[str, np.ndarray], 
                       sr: int, hop_length: int = 512) -> List[Dict]:
        """
        Детекция смеха по характеристикам звука
        
        Смех обычно имеет:
        - Высокий zero crossing rate
        - Определённый паттерн в MFCC
        - Периодические колебания
        """
        if not self.laugh_detection:
            return []
        
        zcr = features['zcr']
        high_zcr_threshold = np.percentile(zcr, 90)
        
        laughs = []
        for i in range(len(zcr)):
            if zcr[i] > high_zcr_threshold:
                time_seconds = i * hop_length / sr
                laughs.append({
                    'time': time_seconds,
                    'score': float(zcr[i] / np.max(zcr)) * 0.8,
                    'type': 'laughter'
                })
        
        return laughs
    
    def detect_screams(self, features: Dict[str, np.ndarray], 
                      sr: int, hop_length: int = 512) -> List[Dict]:
        """
        Детекция криков и восклицаний
        
        Крики обычно имеют:
        - Высокую энергию
        - Высокий spectral centroid
        """
        if not self.scream_detection:
            return []
        
        rms = features['rms']
        centroid = features['spectral_centroid']
        
        # Комбинированный скор
        combined_score = (rms / np.max(rms)) * 0.6 + (centroid / np.max(centroid)) * 0.4
        
        screams = []
        threshold = np.percentile(combined_score, 92)
        
        for i in range(len(combined_score)):
            if combined_score[i] > threshold:
                time_seconds = i * hop_length / sr
                screams.append({
                    'time': time_seconds,
                    'score': float(combined_score[i]),
                    'type': 'scream'
                })
        
        return screams
    
    def cluster_moments(self, moments: List[Dict], max_gap: float = 2.0) -> List[Dict]:
        """
        Кластеризация близких моментов
        
        Args:
            moments: Список обнаруженных моментов
            max_gap: Максимальный разрыв между моментами в секундах
            
        Returns:
            Список кластеризованных моментов
        """
        if not moments:
            return []
        
        # Сортировка по времени
        moments_sorted = sorted(moments, key=lambda x: x['time'])
        
        clusters = []
        current_cluster = [moments_sorted[0]]
        
        for moment in moments_sorted[1:]:
            if moment['time'] - current_cluster[-1]['time'] <= max_gap:
                current_cluster.append(moment)
            else:
                # Сохранение текущего кластера
                avg_time = sum(m['time'] for m in current_cluster) / len(current_cluster)
                max_score = max(m['score'] for m in current_cluster)
                types = list(set(m['type'] for m in current_cluster))
                
                clusters.append({
                    'time': avg_time,
                    'score': max_score,
                    'types': types,
                    'moment_count': len(current_cluster)
                })
                current_cluster = [moment]
        
        # Добавление последнего кластера
        if current_cluster:
            avg_time = sum(m['time'] for m in current_cluster) / len(current_cluster)
            max_score = max(m['score'] for m in current_cluster)
            types = list(set(m['type'] for m in current_cluster))
            
            clusters.append({
                'time': avg_time,
                'score': max_score,
                'types': types,
                'moment_count': len(current_cluster)
            })
        
        return clusters
    
    def analyze(self, video_path: str) -> List[Dict]:
        """
        Полный анализ аудио
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            Список интересных моментов с временными метками
        """
        print("  - Загрузка аудио...")
        audio, sr = self.load_audio(video_path)
        
        if len(audio) == 0:
            print("  - Ошибка: не удалось загрузить аудио")
            return []
        
        print("  - Извлечение признаков...")
        features = self.extract_features(audio, sr)
        
        all_moments = []
        
        # Детекция пиков громкости
        print("  - Поиск пиков громкости...")
        volume_peaks = self.detect_volume_peaks(features, sr)
        all_moments.extend(volume_peaks)
        
        # Детекция смеха
        if self.laugh_detection:
            print("  - Поиск смеха...")
            laughs = self.detect_laughter(features, sr)
            all_moments.extend(laughs)
        
        # Детекция криков
        if self.scream_detection:
            print("  - Поиск криков/восклицаний...")
            screams = self.detect_screams(features, sr)
            all_moments.extend(screams)
        
        # Кластеризация
        print("  - Кластеризация моментов...")
        clustered = self.cluster_moments(all_moments)
        
        # Преобразование в формат с start/end временем
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
                'source': 'audio',
                'types': moment.get('types', ['unknown']),
                'moment_count': moment.get('moment_count', 1)
            })
        
        return result
