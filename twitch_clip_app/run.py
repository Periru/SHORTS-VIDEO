"""
Twitch Clip Generator Pro - Main Entry Point
Запуск приложения
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point"""
    try:
        from src.gui import TwitchClipApp
        app = TwitchClipApp()
        app.mainloop()
    except ImportError as e:
        print("=" * 60)
        print("ОШИБКА: Отсутствуют необходимые зависимости!")
        print("=" * 60)
        print(f"\nДетали ошибки: {e}\n")
        print("Пожалуйста, установите зависимости:")
        print("  pip install -r requirements.txt\n")
        print("Или запустите скрипт установки:")
        print("  Windows: installers/install_windows.bat")
        print("  macOS/Linux: installers/install_unix.sh")
        print("=" * 60)
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        print("=" * 60)
        print("ОШИБКА ПРИ ЗАПУСКЕ!")
        print("=" * 60)
        print(f"\n{e}\n")
        print("Проверьте:")
        print("  1. Установлен ли Python 3.8+")
        print("  2. Установлен ли FFmpeg")
        print("  3. Установлены ли зависимости из requirements.txt")
        print("=" * 60)
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()
