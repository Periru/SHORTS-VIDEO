# ⚡ Краткое руководство по установке

## Для Windows (самый быстрый способ)

### 1️⃣ Скачайте и установите:
- **Python**: [python.org](https://www.python.org/downloads/) ✅ "Add to PATH"
- **FFmpeg**: [ffmpeg.org](https://ffmpeg.org/download.html) → добавьте в PATH

### 2️⃣ Запустите установщик:
Дважды кликните на `installers/install_windows.bat`

### 3️⃣ Запустите программу:
Дважды кликните на `Запустить_TwitchClipGenerator.bat`

---

## Для macOS

### 1️⃣ Установите зависимости:
```bash
brew install python ffmpeg
```

### 2️⃣ Запустите установщик:
```bash
chmod +x installers/install_unix.sh
./installers/install_unix.sh
```

### 3️⃣ Запустите программу:
```bash
./Запустить_TwitchClipGenerator.sh
```

---

## Для Linux

### 1️⃣ Установите зависимости:
```bash
sudo apt update
sudo apt install python3 python3-pip ffmpeg
```

### 2️⃣ Запустите установщик:
```bash
chmod +x installers/install_unix.sh
./installers/install_unix.sh
```

### 3️⃣ Запустите программу:
```bash
./Запустить_TwitchClipGenerator.sh
```

---

## 🎯 Что дальше?

После установки:

1. **Загрузите видео** из Twitch-трансляции
2. **Настройте параметры** (длительность, количество клипов)
3. **Выберите форматы** для экспорта (MP4, MOV, WebM, GIF)
4. **Нажмите "Начать обработку"**
5. **Готово!** Клипы в папке `output/`

---

## ❓ Проблемы?

### "Python не найден"
- Переустановите Python с галочкой "Add Python to PATH"
- Перезапустите компьютер

### "FFmpeg не найден"
- Windows: добавьте `C:\ffmpeg\bin` в PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### Ошибки при установке зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

**Подробная документация:** [README.md](README.md)
