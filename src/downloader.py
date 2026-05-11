"""
Модуль для загрузки видео с Twitch

Поддерживает:
- Загрузку VOD по ID
- Загрузку последнего VOD канала
- Скачивание данных чата
"""

import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import json


class TwitchDownloader:
    """Класс для загрузки контента с Twitch"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client_id = config.get('twitch', {}).get('client_id', '')
        self.oauth_token = config.get('twitch', {}).get('oauth_token', '')
        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': f'OAuth {self.oauth_token}'
        }
        
    def get_user_id(self, channel_name: str) -> Optional[str]:
        """Получение ID пользователя по имени канала"""
        url = f"https://api.twitch.tv/helix/users?login={channel_name}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                return data['data'][0]['id']
            return None
        except Exception as e:
            print(f"Ошибка получения user_id: {e}")
            return None
    
    def get_videos(self, user_id: str, first: int = 1) -> list:
        """Получение списка видео пользователя"""
        url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&first={first}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            print(f"Ошибка получения видео: {e}")
            return []
    
    def download_vod(self, channel: str, video_id: str, output_dir: str = "./temp") -> Optional[str]:
        """
        Загрузка конкретного VOD по ID
        
        Args:
            channel: Имя канала
            video_id: ID видео
            output_dir: Директория для сохранения
            
        Returns:
            Путь к загруженному файлу или None
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Использование youtube-dl или yt-dlp для загрузки
        output_template = str(output_path / f"{channel}_{video_id}.mp4")
        
        cmd = [
            'yt-dlp',
            '--no-playlist',
            '-f', 'best',
            '-o', output_template,
            f'https://www.twitch.tv/videos/{video_id}'
        ]
        
        try:
            print(f"Загрузка VOD {video_id} с канала {channel}...")
            subprocess.run(cmd, check=True)
            
            # Проверка существования файла
            if Path(output_template).exists():
                return output_template
            else:
                # yt-dlp мог добавить расширение
                for f in output_path.glob(f"{channel}_{video_id}.*"):
                    return str(f)
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Ошибка загрузки видео: {e}")
            return None
        except FileNotFoundError:
            print("yt-dlp не найден. Установите: pip install yt-dlp")
            return None
    
    def download_latest_vod(self, channel: str, output_dir: str = "./temp") -> Optional[str]:
        """
        Загрузка последнего VOD с канала
        
        Args:
            channel: Имя канала
            output_dir: Директория для сохранения
            
        Returns:
            Путь к загруженному файлу или None
        """
        user_id = self.get_user_id(channel)
        
        if not user_id:
            print(f"Не удалось получить ID для канала {channel}")
            return None
        
        videos = self.get_videos(user_id, first=1)
        
        if not videos:
            print(f"У канала {channel} нет доступных VOD")
            return None
        
        latest_video = videos[0]
        video_id = latest_video['id']
        
        print(f"Последний VOD: {latest_video.get('title', 'Без названия')}")
        
        return self.download_vod(channel, video_id, output_dir)
    
    def download_chat(self, video_id: str, output_dir: str = "./temp") -> Optional[str]:
        """
        Загрузка данных чата для VOD
        
        Args:
            video_id: ID видео
            output_dir: Директория для сохранения
            
        Returns:
            Путь к JSON файлу с чатом или None
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / f"chat_{video_id}.json"
        
        cmd = [
            'twitch-chat-downloader',
            '-o', str(output_file),
            video_id
        ]
        
        try:
            print(f"Загрузка чата для VOD {video_id}...")
            subprocess.run(cmd, check=True)
            
            if output_file.exists():
                return str(output_file)
            return None
            
        except subprocess.CalledProcessError as e:
            print(f"Ошибка загрузки чата: {e}")
            return None
        except FileNotFoundError:
            print("twitch-chat-downloader не найден. Установите: pip install twitch-chat-downloader")
            return None
    
    def fetch_chat_data(self, channel: str, video_id: str) -> Optional[list]:
        """
        Альтернативный метод получения чата через API
        
        Args:
            channel: Имя канала
            video_id: ID видео
            
        Returns:
            Список сообщений чата или None
        """
        # Для реального использования потребуется подключение к IRC Twitch
        # Это упрощенная версия
        chat_file = self.download_chat(video_id)
        
        if chat_file:
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка чтения чата: {e}")
        
        return None
