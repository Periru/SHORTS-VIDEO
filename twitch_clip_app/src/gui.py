"""
Twitch Clip Generator - Desktop Application
Main entry point for the GUI application
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    import threading
    from src.video_processor import VideoProcessor
    from src.clip_detector import ClipDetector
    from src.config_manager import ConfigManager
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


class TwitchClipApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Twitch Clip Generator Pro")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # State
        self.input_file = None
        self.output_dir = Path("./output")
        self.is_processing = False
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.video_processor = None
        self.clip_detector = None
        
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎬 Twitch Clip Generator Pro",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Автоматическое создание вирусных клипов для TikTok и YouTube Shorts",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack()
        
        # Main content area
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Input & Settings
        left_panel = ctk.CTkScrollableFrame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.create_input_section(left_panel)
        self.create_settings_section(left_panel)
        self.create_format_section(left_panel)
        
        # Right panel - Preview & Output
        right_panel = ctk.CTkScrollableFrame(main_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.create_preview_section(right_panel)
        self.create_output_section(right_panel)
        self.create_log_section(right_panel)
        
        # Bottom action bar
        self.create_action_bar()
        
    def create_input_section(self, parent):
        """Create input file section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text="📁 Входной файл", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.input_label = ctk.CTkLabel(
            frame, 
            text="Файл не выбран",
            text_color="gray",
            wraplength=400
        )
        self.input_label.pack(anchor="w", padx=15, pady=5)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=15, pady=5)
        
        self.btn_load_video = ctk.CTkButton(
            btn_frame,
            text="Загрузить видео",
            command=self.load_video,
            width=150
        )
        self.btn_load_video.pack(side="left", padx=(0, 10))
        
        self.btn_load_twitch = ctk.CTkButton(
            btn_frame,
            text="Загрузить с Twitch",
            command=self.load_from_twitch,
            width=150
        )
        self.btn_load_twitch.pack(side="left")
        
    def create_settings_section(self, parent):
        """Create settings section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text="⚙️ Настройки", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Duration
        duration_frame = ctk.CTkFrame(frame, fg_color="transparent")
        duration_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(duration_frame, text="Длительность клипа (сек):").pack(anchor="w")
        self.duration_slider = ctk.CTkSlider(
            duration_frame,
            from_=15,
            to=180,
            number_of_steps=33,
            command=lambda x: self.duration_label.configure(text=f"{int(x)} сек")
        )
        self.duration_slider.set(60)
        self.duration_slider.pack(fill="x", pady=5)
        
        self.duration_label = ctk.CTkLabel(duration_frame, text="60 сек")
        self.duration_label.pack(anchor="w")
        
        # Max clips
        clips_frame = ctk.CTkFrame(frame, fg_color="transparent")
        clips_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(clips_frame, text="Максимум клипов:").pack(anchor="w")
        self.max_clips_slider = ctk.CTkSlider(
            clips_frame,
            from_=1,
            to=20,
            number_of_steps=19,
            command=lambda x: self.max_clips_label.configure(text=f"{int(x)}")
        )
        self.max_clips_slider.set(5)
        self.max_clips_slider.pack(fill="x", pady=5)
        
        self.max_clips_label = ctk.CTkLabel(clips_frame, text="5")
        self.max_clips_label.pack(anchor="w")
        
        # Sensitivity
        sens_frame = ctk.CTkFrame(frame, fg_color="transparent")
        sens_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(sens_frame, text="Чувствительность детекции:").pack(anchor="w")
        self.sensitivity_slider = ctk.CTkSlider(
            sens_frame,
            from_=0.3,
            to=0.9,
            number_of_steps=12,
            command=lambda x: self.sensitivity_label.configure(text=f"{x:.2f}")
        )
        self.sensitivity_slider.set(0.6)
        self.sensitivity_slider.pack(fill="x", pady=5)
        
        self.sensitivity_label = ctk.CTkLabel(sens_frame, text="0.60")
        self.sensitivity_label.pack(anchor="w")
        
        # Options
        self.chk_subtitles = ctk.CTkCheckBox(frame, text="Генерировать субтитры")
        self.chk_subtitles.pack(anchor="w", padx=15, pady=5)
        self.chk_subtitles.select()
        
        self.chk_auto_crop = ctk.CTkCheckBox(frame, text="Авто-кадрирование 9:16")
        self.chk_auto_crop.pack(anchor="w", padx=15, pady=5)
        self.chk_auto_crop.select()
        
        self.chk_enhance_audio = ctk.CTkCheckBox(frame, text="Улучшение аудио")
        self.chk_enhance_audio.pack(anchor="w", padx=15, pady=5)
        
    def create_format_section(self, parent):
        """Create output format section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text="📤 Форматы экспорта", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.format_vars = {}
        formats = [
            ("mp4_h264", "MP4 (H.264) - Универсальный"),
            ("mp4_hevc", "MP4 (HEVC) - Высокое качество"),
            ("mov", "MOV - Для монтажа"),
            ("webm", "WebM - Для веба"),
            ("gif", "GIF - Анимация")
        ]
        
        for key, text in formats:
            chk = ctk.CTkCheckBox(frame, text=text)
            chk.pack(anchor="w", padx=15, pady=3)
            if key == "mp4_h264":
                chk.select()
            self.format_vars[key] = chk
            
    def create_preview_section(self, parent):
        """Create preview section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, pady=10)
        
        label = ctk.CTkLabel(frame, text="🎥 Предпросмотр", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.preview_label = ctk.CTkLabel(
            frame,
            text="Загрузите видео для предпросмотра",
            text_color="gray"
        )
        self.preview_label.pack(expand=True, pady=40)
        
        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.pack(fill="x", padx=15, pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(frame, text="Готов к работе", text_color="gray")
        self.status_label.pack(pady=5)
        
    def create_output_section(self, parent):
        """Create output section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text="💾 Выходная папка", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.output_label = ctk.CTkLabel(
            frame,
            text=str(self.output_dir.absolute()),
            text_color="gray",
            wraplength=400
        )
        self.output_label.pack(anchor="w", padx=15, pady=5)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Изменить папку",
            command=self.change_output_dir,
            width=150
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Открыть папку",
            command=self.open_output_dir,
            width=150,
            fg_color="gray"
        ).pack(side="left", padx=10)
        
    def create_log_section(self, parent):
        """Create log section"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, pady=10)
        
        label = ctk.CTkLabel(frame, text="📋 Журнал операций", font=ctk.CTkFont(weight="bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=15, pady=5)
        self.log_text.insert("0.0", "Приложение готово к работе...\n")
        self.log_text.configure(state="disabled")
        
    def create_action_bar(self):
        """Create bottom action bar"""
        frame = ctk.CTkFrame(self)
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        self.btn_start = ctk.CTkButton(
            frame,
            text="🚀 Начать обработку",
            command=self.start_processing,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.btn_start.pack(side="left", padx=10)
        
        self.btn_cancel = ctk.CTkButton(
            frame,
            text="❌ Отмена",
            command=self.cancel_processing,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.btn_cancel.pack(side="left", padx=10)
        
        stats_frame = ctk.CTkFrame(frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=10)
        
        self.clips_found_label = ctk.CTkLabel(stats_frame, text="Найдено клипов: 0")
        self.clips_found_label.pack()
        
        self.time_remaining_label = ctk.CTkLabel(stats_frame, text="Осталось: --:--")
        self.time_remaining_label.pack()
        
    def load_video(self):
        """Load video file"""
        filetypes = [
            ("Видео файлы", "*.mp4 *.avi *.mov *.mkv *.flv *.webm"),
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Выберите видео файл",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file = Path(filename)
            self.input_label.configure(text=str(self.input_file.name))
            self.log(f"Загружен файл: {self.input_file.name}")
            self.update_preview()
            
    def load_from_twitch(self):
        """Load from Twitch URL"""
        dialog = ctk.CTkInputDialog(
            title="Загрузка с Twitch",
            text="Вставьте ссылку на трансляцию или видео Twitch:"
        )
        
        url = dialog.get_input()
        if url:
            self.log(f"Загрузка с Twitch: {url}")
            self.status_label.configure(text="Загрузка с Twitch...")
            # TODO: Implement Twitch download
            messagebox.showinfo("Инфо", "Функция загрузки с Twitch будет доступна в следующей версии")
            
    def change_output_dir(self):
        """Change output directory"""
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if directory:
            self.output_dir = Path(directory)
            self.output_label.configure(text=str(self.output_dir))
            self.log(f"Папка вывода изменена: {self.output_dir}")
            
    def open_output_dir(self):
        """Open output directory"""
        if self.output_dir.exists():
            os.startfile(self.output_dir) if sys.platform == "win32" else \
            os.system(f"open {self.output_dir}") if sys.platform == "darwin" else \
            os.system(f"xdg-open {self.output_dir}")
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
    def update_preview(self):
        """Update preview"""
        if self.input_file:
            self.preview_label.configure(text=f"📹 {self.input_file.name}\nГотов к обработке")
            
    def start_processing(self):
        """Start processing"""
        if not self.input_file:
            messagebox.showwarning("Предупреждение", "Сначала загрузите видео файл!")
            return
            
        if self.is_processing:
            return
            
        self.is_processing = True
        self.btn_start.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        
        # Get settings
        duration = int(self.duration_slider.get())
        max_clips = int(self.max_clips_slider.get())
        sensitivity = self.sensitivity_slider.get()
        add_subtitles = self.chk_subtitles.get()
        auto_crop = self.chk_auto_crop.get()
        enhance_audio = self.chk_enhance_audio.get()
        
        formats = [key for key, chk in self.format_vars.items() if chk.get()]
        
        self.log("=" * 50)
        self.log("НАЧАЛО ОБРАБОТКИ")
        self.log(f"Файл: {self.input_file.name}")
        self.log(f"Длительность клипа: {duration} сек")
        self.log(f"Максимум клипов: {max_clips}")
        self.log(f"Чувствительность: {sensitivity}")
        self.log(f"Форматы: {', '.join(formats)}")
        self.log("=" * 50)
        
        # Start processing in thread
        thread = threading.Thread(
            target=self.process_video,
            args=(duration, max_clips, sensitivity, add_subtitles, auto_crop, enhance_audio, formats)
        )
        thread.daemon = True
        thread.start()
        
    def process_video(self, duration, max_clips, sensitivity, subtitles, crop, enhance, formats):
        """Process video in background thread"""
        try:
            # Initialize processors
            self.video_processor = VideoProcessor(str(self.input_file))
            self.clip_detector = ClipDetector(sensitivity=sensitivity)
            
            self.log("Анализ видео...")
            self.after(0, lambda: self.status_label.configure(text="Анализ видео..."))
            
            # Detect clips
            potential_clips = self.clip_detector.detect_clips(str(self.input_file))
            
            if not potential_clips:
                self.after(0, lambda: messagebox.showinfo("Результат", "Не найдено подходящих фрагментов"))
                return
                
            self.log(f"Найдено потенциальных клипов: {len(potential_clips)}")
            self.after(0, lambda: self.clips_found_label.configure(text=f"Найдено клипов: {len(potential_clips)}"))
            
            # Select top clips
            selected_clips = sorted(potential_clips, key=lambda x: x['score'], reverse=True)[:max_clips]
            
            self.log(f"Отобрано лучших клипов: {len(selected_clips)}")
            
            # Process each clip
            for i, clip in enumerate(selected_clips):
                progress = (i + 1) / len(selected_clips)
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda c=i+1, t=len(selected_clips): 
                    self.status_label.configure(text=f"Обработка клипа {c}/{t}"))
                
                self.log(f"Создание клипа {i+1}/{len(selected_clips)}...")
                
                # Extract and process clip
                clip_output = self.video_processor.extract_clip(
                    clip['start'],
                    clip['end'],
                    duration=duration,
                    output_dir=str(self.output_dir),
                    add_subtitles=subtitles,
                    auto_crop=crop,
                    enhance_audio=enhance
                )
                
                # Convert to formats
                for fmt in formats:
                    self.log(f"Конвертация в {fmt}...")
                    self.video_processor.convert_format(clip_output, fmt, str(self.output_dir))
                    
                self.log(f"✅ Клип {i+1} готов")
                
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.status_label.configure(text="✅ Обработка завершена!"))
            self.after(0, lambda: messagebox.showinfo("Готово", f"Создано {len(selected_clips)} клипов!\nПапка: {self.output_dir}"))
            self.log("=" * 50)
            self.log("ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО")
            
        except Exception as e:
            self.log(f"❌ Ошибка: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}"))
            
        finally:
            self.is_processing = False
            self.after(0, lambda: self.btn_start.configure(state="normal"))
            self.after(0, lambda: self.btn_cancel.configure(state="disabled"))
            
    def cancel_processing(self):
        """Cancel processing"""
        if messagebox.askyesno("Подтверждение", "Отменить обработку?"):
            self.is_processing = False
            self.log("Обработка отменена пользователем")
            
    def log(self, message):
        """Add message to log"""
        self.log_text.configure(state="normal")
        timestamp = Path(__file__).stem  # Simple timestamp
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


def main():
    app = TwitchClipApp()
    app.mainloop()


if __name__ == "__main__":
    main()
