"""
Модуль для анализа активности чата Twitch

Обнаруживает:
- Всплески активности чата
- Хайповые эмодзи
- Мемные фразы
- Реакции на важные события
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import defaultdict


class ChatAnalyzer:
    """Класс для анализа чата Twitch"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hype_multiplier = config.get('chat', {}).get('hype_multiplier', 1.5)
        self.emote_priority = config.get('chat', {}).get('emote_priority', [
            'PogChamp', 'Kappa', 'LUL', 'OMEGALUL', 'monkaS'
        ])
        
        # Мемные фразы и их веса
        self.meme_phrases = {
            'LETSGO': 1.5,
            'POG': 1.4,
            'POGGERS': 1.4,
            'WOW': 1.2,
            'OMG': 1.3,
            'WHAT': 1.2,
            'NO WAY': 1.4,
            'HOLY': 1.3,
            'CLUTCH': 1.5,
            'INSANE': 1.4,
            'CRITICAL': 1.3,
            'FAIL': 1.2,
            'LOL': 1.1,
            'LMAO': 1.2,
            'KEKW': 1.3,
        }
    
    def load_chat_data(self, chat_file: str) -> Optional[List[Dict]]:
        """
        Загрузка данных чата из JSON файла
        
        Args:
            chat_file: Путь к JSON файлу с чатом
            
        Returns:
            Список сообщений или None
        """
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки чата: {e}")
            return None
    
    def analyze_activity(self, chat_data: List[Dict], 
                        window_size: float = 5.0) -> List[Dict]:
        """
        Анализ активности чата по временным окнам
        
        Args:
            chat_data: Список сообщений чата
            window_size: Размер окна в секундах
            
        Returns:
            Список периодов с высокой активностью
        """
        if not chat_data:
            return []
        
        # Извлечение временных меток
        timestamps = []
        for msg in chat_data:
            # Предполагаем формат с полем 'timestamp' в секундах
            if 'timestamp' in msg:
                timestamps.append(msg['timestamp'])
            elif 't' in msg:  # Формат twitch-chat-downloader
                timestamps.append(msg['t'])
        
        if not timestamps:
            return []
        
        timestamps.sort()
        
        # Подсчёт сообщений в скользящем окне
        activity_windows = defaultdict(int)
        
        for ts in timestamps:
            window_key = int(ts / window_size)
            activity_windows[window_key] += 1
        
        # Нахождение пиков активности
        if not activity_windows:
            return []
        
        max_activity = max(activity_windows.values())
        avg_activity = sum(activity_windows.values()) / len(activity_windows)
        
        peaks = []
        threshold = avg_activity * 2  # В 2 раза выше среднего
        
        for window_key, count in activity_windows.items():
            if count > threshold:
                center_time = (window_key + 0.5) * window_size
                normalized_score = count / max_activity
                
                peaks.append({
                    'time': center_time,
                    'score': normalized_score,
                    'message_count': count,
                    'type': 'activity_spike'
                })
        
        return peaks
    
    def detect_hype_emotes(self, chat_data: List[Dict]) -> List[Dict]:
        """
        Детекция моментов с хайповыми эмодзи
        
        Args:
            chat_data: Список сообщений чата
            
        Returns:
            Список моментов с эмодзи
        """
        emote_moments = defaultdict(lambda: {'count': 0, 'emotes': []})
        
        for msg in chat_data:
            timestamp = msg.get('timestamp', msg.get('t', 0))
            message = msg.get('message', msg.get('msg', '')).upper()
            
            # Проверка на приоритетные эмодзи
            for emote in self.emote_priority:
                if emote.upper() in message:
                    window_key = int(timestamp / 5)
                    emote_moments[window_key]['count'] += 1
                    emote_moments[window_key]['emotes'].append(emote)
                    emote_moments[window_key]['timestamp'] = timestamp
        
        # Преобразование в формат моментов
        moments = []
        for window_key, data in emote_moments.items():
            if data['count'] >= 2:  # Минимум 2 эмодзи
                center_time = (window_key + 0.5) * 5
                unique_emotes = list(set(data['emotes']))
                
                score = min(1.0, data['count'] / 10) * self.hype_multiplier
                
                moments.append({
                    'time': center_time,
                    'score': score,
                    'emote_count': data['count'],
                    'emotes': unique_emotes,
                    'type': 'hype_emote'
                })
        
        return moments
    
    def detect_meme_phrases(self, chat_data: List[Dict]) -> List[Dict]:
        """
        Детекция мемных фраз в чате
        
        Args:
            chat_data: Список сообщений чата
            
        Returns:
            Список моментов с мемными фразами
        """
        phrase_moments = defaultdict(lambda: {'count': 0, 'phrases': [], 'weight': 0})
        
        for msg in chat_data:
            timestamp = msg.get('timestamp', msg.get('t', 0))
            message = msg.get('message', msg.get('msg', '')).upper()
            
            # Проверка на мемные фразы
            for phrase, weight in self.meme_phrases.items():
                if phrase in message:
                    window_key = int(timestamp / 5)
                    phrase_moments[window_key]['count'] += 1
                    phrase_moments[window_key]['phrases'].append(phrase)
                    phrase_moments[window_key]['weight'] += weight
                    phrase_moments[window_key]['timestamp'] = timestamp
        
        # Преобразование в формат моментов
        moments = []
        for window_key, data in phrase_moments.items():
            if data['count'] >= 2:
                center_time = (window_key + 0.5) * 5
                unique_phrases = list(set(data['phrases']))
                
                # Нормализация веса
                max_possible_weight = len(self.meme_phrases) * 2
                normalized_weight = min(1.0, data['weight'] / max_possible_weight)
                
                moments.append({
                    'time': center_time,
                    'score': normalized_weight,
                    'phrase_count': data['count'],
                    'phrases': unique_phrases,
                    'type': 'meme_phrase'
                })
        
        return moments
    
    def cluster_moments(self, moments: List[Dict], 
                       max_gap: float = 10.0) -> List[Dict]:
        """
        Кластеризация близких моментов чата
        
        Args:
            moments: Список обнаруженных моментов
            max_gap: Максимальный разрыв между моментами
            
        Returns:
            Список кластеризованных моментов
        """
        if not moments:
            return []
        
        moments_sorted = sorted(moments, key=lambda x: x['time'])
        
        clusters = []
        current_cluster = moments_sorted[0:1]
        
        for moment in moments_sorted[1:]:
            last_time = current_cluster[-1].get('time', 
                          current_cluster[-1].get('timestamp', 0))
            curr_time = moment.get('time', moment.get('timestamp', 0))
            
            if curr_time - last_time <= max_gap:
                current_cluster.append(moment)
            else:
                # Сохранение кластера
                avg_time = sum(m.get('time', m.get('timestamp', 0)) 
                              for m in current_cluster) / len(current_cluster)
                max_score = max(m['score'] for m in current_cluster)
                
                all_types = []
                all_emotes = []
                all_phrases = []
                
                for m in current_cluster:
                    if m.get('type') == 'hype_emote':
                        all_emotes.extend(m.get('emotes', []))
                    elif m.get('type') == 'meme_phrase':
                        all_phrases.extend(m.get('phrases', []))
                    all_types.append(m.get('type', 'unknown'))
                
                clusters.append({
                    'time': avg_time,
                    'score': max_score,
                    'types': list(set(all_types)),
                    'emotes': list(set(all_emotes)),
                    'phrases': list(set(all_phrases)),
                    'moment_count': len(current_cluster)
                })
                current_cluster = [moment]
        
        # Последний кластер
        if current_cluster:
            avg_time = sum(m.get('time', m.get('timestamp', 0)) 
                          for m in current_cluster) / len(current_cluster)
            max_score = max(m['score'] for m in current_cluster)
            
            all_types = [m.get('type', 'unknown') for m in current_cluster]
            
            clusters.append({
                'time': avg_time,
                'score': max_score,
                'types': list(set(all_types)),
                'moment_count': len(current_cluster)
            })
        
        return clusters
    
    def analyze(self, channel: str, video_id: str, 
               chat_file: Optional[str] = None) -> List[Dict]:
        """
        Полный анализ чата
        
        Args:
            channel: Имя канала
            video_id: ID видео
            chat_file: Опциональный путь к файлу чата
            
        Returns:
            Список интересных моментов
        """
        print("  - Загрузка данных чата...")
        
        # Если файл не указан, пытаемся загрузить стандартным путём
        if not chat_file:
            chat_file = f"./temp/chat_{video_id}.json"
        
        if not Path(chat_file).exists():
            print(f"  - Файл чата не найден: {chat_file}")
            print("  - Пропускаем анализ чата")
            return []
        
        chat_data = self.load_chat_data(chat_file)
        
        if not chat_data:
            return []
        
        print(f"  - Загружено {len(chat_data)} сообщений")
        
        all_moments = []
        
        # Анализ активности
        print("  - Анализ всплесков активности...")
        activity_peaks = self.analyze_activity(chat_data)
        all_moments.extend(activity_peaks)
        print(f"    Найдено {len(activity_peaks)} пиков активности")
        
        # Детекция хайповых эмодзи
        print("  - Поиск хайповых эмодзи...")
        hype_emotes = self.detect_hype_emotes(chat_data)
        all_moments.extend(hype_emotes)
        print(f"    Найдено {len(hype_emotes)} моментов с эмодзи")
        
        # Детекция мемных фраз
        print("  - Поиск мемных фраз...")
        meme_phrases = self.detect_meme_phrases(chat_data)
        all_moments.extend(meme_phrases)
        print(f"    Найдено {len(meme_phrases)} моментов с фразами")
        
        # Кластеризация
        print("  - Кластеризация моментов...")
        clustered = self.cluster_moments(all_moments)
        
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
                'source': 'chat',
                'types': moment.get('types', ['activity']),
                'emotes': moment.get('emotes', []),
                'phrases': moment.get('phrases', []),
                'moment_count': moment.get('moment_count', 1)
            })
        
        return result
