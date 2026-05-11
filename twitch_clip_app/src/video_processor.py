"""
Video Processor Module
Handles video extraction, cropping, and format conversion
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, List


class VideoProcessor:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.video_info = self._get_video_info()
        
    def _get_video_info(self) -> dict:
        """Get video information using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', self.input_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Parse JSON output (simplified)
            return {'duration': 0, 'width': 1920, 'height': 1080}
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {'duration': 0, 'width': 1920, 'height': 1080}
    
    def extract_clip(self, start_time: float, end_time: float, 
                     duration: int = 60, output_dir: str = "./output",
                     add_subtitles: bool = False, auto_crop: bool = True,
                     enhance_audio: bool = False) -> str:
        """Extract a clip from the video"""
        output_path = Path(output_dir) / f"clip_{start_time:.0f}_{end_time:.0f}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate actual duration
        clip_duration = min(end_time - start_time, duration)
        
        # Build FFmpeg command
        cmd = ['ffmpeg', '-y', '-i', self.input_path]
        
        # Time options
        cmd.extend(['-ss', str(start_time), '-t', str(clip_duration)])
        
        # Video filters
        filters = []
        if auto_crop:
            # Crop to 9:16 vertical format
            filters.append('crop=ih*(9/16):ih')
            
        if enhance_audio:
            # Audio enhancement will be handled separately
        
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        # Audio options
        if enhance_audio:
            cmd.extend(['-af', 'loudnorm,volume=1.5'])
        
        # Output settings
        cmd.extend([
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            str(output_path)
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Clip extracted: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"Error extracting clip: {e}")
            raise
    
    def convert_format(self, input_file: str, format_type: str, 
                       output_dir: str = "./output") -> str:
        """Convert video to different format"""
        input_path = Path(input_file)
        base_name = input_path.stem
        
        format_configs = {
            'mp4_h264': {
                'ext': 'mp4',
                'cmd': ['-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-c:a', 'aac']
            },
            'mp4_hevc': {
                'ext': 'mp4',
                'cmd': ['-c:v', 'libx265', '-preset', 'medium', '-crf', '28', '-c:a', 'aac']
            },
            'mov': {
                'ext': 'mov',
                'cmd': ['-c:v', 'prores', '-profile', '3', '-c:a', 'pcm_s16le']
            },
            'webm': {
                'ext': 'webm',
                'cmd': ['-c:v', 'libvpx-vp9', '-b:v', '2M', '-c:a', 'libopus']
            },
            'gif': {
                'ext': 'gif',
                'cmd': ['-vf', 'fps=10,scale=480:-1:flags=lanczos', '-loop', '0']
            }
        }
        
        if format_type not in format_configs:
            raise ValueError(f"Unknown format: {format_type}")
        
        config = format_configs[format_type]
        output_path = Path(output_dir) / f"{base_name}.{config['ext']}"
        
        cmd = ['ffmpeg', '-y', '-i', input_file] + config['cmd'] + [str(output_path)]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Converted to {format_type}: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"Error converting format: {e}")
            raise
    
    def add_subtitles(self, video_path: str, subtitle_text: str, 
                      output_path: Optional[str] = None) -> str:
        """Add subtitles to video (simplified version)"""
        if output_path is None:
            output_path = Path(video_path).parent / f"{Path(video_path).stem}_sub.mp4"
        
        # Create temporary subtitle file
        sub_file = Path(output_path).parent / "temp.srt"
        with open(sub_file, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\n")
            f.write(subtitle_text + "\n")
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"subtitles={sub_file}",
            '-c:a', 'copy', str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            sub_file.unlink()  # Remove temp file
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"Error adding subtitles: {e}")
            raise
