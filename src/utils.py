"""
Утилиты для Twitch Clip Generator

Вспомогательные функции:
- Скоринг и выбор лучших моментов
- Объединение данных из разных источников
- Вспомогательные вычисления
"""

from typing import List, Dict, Any
import numpy as np


def normalize_score(score: float, min_val: float = 0, max_val: float = 1) -> float:
    """
    Нормализация скоринга
    
    Args:
        score: Исходный скор
        min_val: Минимальное значение
        max_val: Максимальное значение
        
    Returns:
        Нормализованный скор (0.0-1.0)
    """
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (score - min_val) / (max_val - min_val)))


def calculate_moment_score(moment: Dict, weights: Dict[str, float] = None) -> float:
    """
    Расчёт комплексного скоринга для момента
    
    Args:
        moment: Словарь с данными момента
        weights: Веса для различных факторов
        
    Returns:
        Итоговый скор момента
    """
    if weights is None:
        weights = {
            'audio': 0.4,
            'chat': 0.35,
            'emotion': 0.25
        }
    
    base_score = moment.get('score', 0.5)
    source = moment.get('source', 'unknown')
    
    # Бонус за множественные детекции
    moment_count = moment.get('moment_count', 1)
    count_bonus = min(0.2, moment_count * 0.05)
    
    # Бонус за тип момента
    type_bonus = 0.0
    types = moment.get('types', [])
    
    if 'laughter' in types or 'joy' in types:
        type_bonus += 0.1
    if 'scream' in types or 'surprise' in types:
        type_bonus += 0.1
    if 'hype_emote' in types:
        type_bonus += 0.15
    if 'meme_phrase' in types:
        type_bonus += 0.15
    
    # Проверка эмодзи
    emotes = moment.get('emotes', [])
    priority_emotes = ['PogChamp', 'OMEGALUL', 'monkaS', 'LUL']
    for emote in emotes:
        if emote in priority_emotes:
            type_bonus += 0.1
            break
    
    # Итоговый скор
    final_score = base_score + count_bonus + type_bonus
    
    return min(1.0, final_score)


def merge_overlapping_moments(moments: List[Dict], 
                              overlap_threshold: float = 10.0) -> List[Dict]:
    """
    Слияние перекрывающихся моментов
    
    Args:
        moments: Список моментов
        overlap_threshold: Порог перекрытия в секундах
        
    Returns:
        Список неперекрывающихся моментов
    """
    if len(moments) <= 1:
        return moments
    
    # Сортировка по времени начала
    sorted_moments = sorted(moments, key=lambda x: x['start_time'])
    
    merged = []
    current = sorted_moments[0].copy()
    
    for moment in sorted_moments[1:]:
        # Проверка на перекрытие
        if moment['start_time'] <= current['end_time'] + overlap_threshold:
            # Слияние
            current['end_time'] = max(current['end_time'], moment['end_time'])
            current['score'] = max(current['score'], moment['score'])
            
            # Объединение типов и источников
            if 'types' not in current:
                current['types'] = []
            if 'types' in moment:
                current['types'].extend(moment['types'])
                current['types'] = list(set(current['types']))
            
            if 'source' not in current:
                current['sources'] = [current.get('source', 'unknown')]
            if 'sources' not in current:
                current['sources'] = [current.get('source', 'unknown')]
            current['sources'].append(moment.get('source', 'unknown'))
            current['sources'] = list(set(current['sources']))
            
            # Обновление момента центра
            current['center_time'] = (current['start_time'] + current['end_time']) / 2
        else:
            # Сохранение текущего и переход к следующему
            merged.append(current)
            current = moment.copy()
    
    # Добавление последнего момента
    merged.append(current)
    
    return merged


def score_and_select_moments(moments: List[Dict],
                            clip_duration: float = 60,
                            max_clips: int = 5,
                            min_score: float = 0.7) -> List[Dict]:
    """
    Скоринг и выбор лучших моментов
    
    Args:
        moments: Все обнаруженные моменты
        clip_duration: Длительность клипа в секундах
        max_clips: Максимальное количество клипов
        min_score: Минимальный порог качества
        
    Returns:
        Список лучших моментов
    """
    if not moments:
        return []
    
    print(f"  - Обработка {len(moments)} моментов...")
    
    # Расчёт скоринга для каждого момента
    scored_moments = []
    for moment in moments:
        score = calculate_moment_score(moment)
        
        scored_moment = {
            **moment,
            'final_score': score
        }
        scored_moments.append(scored_moment)
    
    # Сортировка по скору
    scored_moments.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Слияние перекрывающихся
    merged = merge_overlapping_moments(scored_moments)
    
    # Фильтрация по минимальному скору
    filtered = [m for m in merged if m['final_score'] >= min_score]
    
    # Дополнительная сортировка после слияния
    filtered.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Выбор топ-N с проверкой на перекрытия
    selected = []
    for moment in filtered:
        if len(selected) >= max_clips:
            break
        
        # Проверка на перекрытие с уже выбранными
        overlaps = False
        for selected_moment in selected:
            if (moment['start_time'] < selected_moment['end_time'] and
                moment['end_time'] > selected_moment['start_time']):
                overlaps = True
                break
        
        if not overlaps:
            selected.append(moment)
    
    # Если выбрали меньше чем нужно, добавляем следующие лучшие
    if len(selected) < max_clips:
        for moment in filtered:
            if len(selected) >= max_clips:
                break
            if moment not in selected:
                selected.append(moment)
    
    # Финальная корректировка start/end времени
    half_duration = clip_duration / 2
    for moment in selected:
        center = moment.get('center_time', moment.get('time', 0))
        moment['start_time'] = max(0, center - half_duration)
        moment['end_time'] = center + half_duration
    
    print(f"  - Выбрано {len(selected)} лучших моментов")
    
    return selected


def format_timestamp(seconds: float) -> str:
    """
    Форматирование временной метки в человекочитаемый вид
    
    Args:
        seconds: Время в секундах
        
    Returns:
        Строка в формате HH:MM:SS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_video_duration(video_path: str) -> float:
    """
    Получение длительности видео
    
    Args:
        video_path: Путь к видеофайлу
        
    Returns:
        Длительность в секундах
    """
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Ошибка получения длительности: {e}")
        return 0.0


def create_summary_report(moments: List[Dict], output_path: str = None) -> str:
    """
    Создание отчёта о найденных моментах
    
    Args:
        moments: Список моментов
        output_path: Путь для сохранения отчёта
        
    Returns:
        Текст отчёта
    """
    report_lines = [
        "=" * 60,
        "Twitch Clip Generator - Отчёт",
        "=" * 60,
        "",
        f"Всего найдено моментов: {len(moments)}",
        ""
    ]
    
    for i, moment in enumerate(moments, 1):
        start_fmt = format_timestamp(moment['start_time'])
        end_fmt = format_timestamp(moment['end_time'])
        score = moment.get('final_score', moment.get('score', 0))
        
        report_lines.append(f"Момент #{i}")
        report_lines.append(f"  Время: {start_fmt} - {end_fmt}")
        report_lines.append(f"  Скор: {score:.2f}")
        report_lines.append(f"  Источник: {moment.get('source', 'unknown')}")
        
        if 'types' in moment:
            report_lines.append(f"  Типы: {', '.join(moment['types'])}")
        if 'emotes' in moment:
            report_lines.append(f"  Эмодзи: {', '.join(moment['emotes'])}")
        if 'phrases' in moment:
            report_lines.append(f"  Фразы: {', '.join(moment['phrases'])}")
        
        report_lines.append("")
    
    report = "\n".join(report_lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Отчёт сохранён: {output_path}")
    
    return report
