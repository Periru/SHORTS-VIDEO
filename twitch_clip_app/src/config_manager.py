"""
Configuration Manager Module
Handles application settings and preferences
"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'app': {
                'name': 'Twitch Clip Generator Pro',
                'version': '1.0.0',
                'language': 'ru'
            },
            'processing': {
                'default_duration': 60,
                'max_clips': 5,
                'sensitivity': 0.6,
                'auto_crop': True,
                'add_subtitles': True,
                'enhance_audio': False
            },
            'output': {
                'directory': './output',
                'formats': ['mp4_h264'],
                'naming_pattern': '{streamer}_{date}_{time}'
            },
            'twitch': {
                'client_id': '',
                'oauth_token': '',
                'download_quality': 'best'
            },
            'ai': {
                'use_whisper': True,
                'whisper_model': 'base',
                'detect_faces': True,
                'detect_emotions': True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    # Merge with defaults
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            # Save default config
            self._save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        default_config = {
            'app': {
                'name': 'Twitch Clip Generator Pro',
                'version': '1.0.0',
                'language': 'ru'
            },
            'processing': {
                'default_duration': 60,
                'max_clips': 5,
                'sensitivity': 0.6,
                'auto_crop': True,
                'add_subtitles': True,
                'enhance_audio': False
            },
            'output': {
                'directory': './output',
                'formats': ['mp4_h264'],
                'naming_pattern': '{streamer}_{date}_{time}'
            },
            'twitch': {
                'client_id': '',
                'oauth_token': '',
                'download_quality': 'best'
            },
            'ai': {
                'use_whisper': True,
                'whisper_model': 'base',
                'detect_faces': True,
                'detect_emotions': True
            }
        }
        self.config = default_config
        self._save_config(default_config)
