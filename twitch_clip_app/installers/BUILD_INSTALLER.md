# 📦 Создание установщика для Windows

Этот файл содержит инструкции по созданию полноценного установщика (.exe) для программы.

## Вариант 1: PyInstaller (быстрый способ)

### Установка:
```bash
pip install pyinstaller
```

### Сборка:
```bash
# Перейдите в папку проекта
cd twitch_clip_app

# Создайте .exe файл
pyinstaller --onefile --windowed --name "TwitchClipGenerator" src/gui.py
```

Готовый файл: `dist/TwitchClipGenerator.exe`

### Продвинутая сборка с иконкой:
```bash
pyinstaller --onefile --windowed --name "TwitchClipGenerator" --icon=assets/icon.ico --add-data "src;src" src/gui.py
```

## Вариант 2: Inno Setup (профессиональный установщик)

### Шаг 1: Установка Inno Setup
Скачайте с: https://jrsoftware.org/isdl.php

### Шаг 2: Создайте скрипт setup.iss

```pascal
[Setup]
AppName=Twitch Clip Generator Pro
AppVersion=1.0.0
DefaultDirName={pf}\TwitchClipGenerator
DefaultGroupName=Twitch Clip Generator
OutputBaseFilename=TwitchClipGenerator_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\TwitchClipGenerator.exe"; DestDir: "{app}"
Source: "ffmpeg.exe"; DestDir: "{app}"
Source: "ffprobe.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Twitch Clip Generator"; Filename: "{app}\TwitchClipGenerator.exe"
Name: "{autodesktop}\Twitch Clip Generator"; Filename: "{app}\TwitchClipGenerator.exe"

[Run]
Filename: "{app}\TwitchClipGenerator.exe"; Description: "Запустить программу"; Flags: nowait postinstall skipifsilent
```

### Шаг 3: Компиляция
Откройте setup.iss в Inno Setup Compiler и нажмите "Build"

## Вариант 3: NSIS (альтернатива Inno Setup)

### Скрипт installer.nsi:
```nsis
!include "MUI2.nsh"

Name "Twitch Clip Generator Pro"
OutFile "TwitchClipGenerator_Installer.exe"
InstallDir "$PROGRAMFILES\TwitchClipGenerator"

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Russian"

Section "Install"
  SetOutPath $INSTDIR
  File "dist\TwitchClipGenerator.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  CreateDirectory "$SMPROGRAMS\Twitch Clip Generator"
  CreateShortcut "$SMPROGRAMS\Twitch Clip Generator\Twitch Clip Generator.lnk" "$INSTDIR\TwitchClipGenerator.exe"
  CreateShortcut "$DESKTOP\Twitch Clip Generator.lnk" "$INSTDIR\TwitchClipGenerator.exe"
SectionEnd
```

## Добавление FFmpeg в установщик

Для автономной работы рекомендуется включить FFmpeg в установщик:

1. Скачайте FFmpeg с ffmpeg.org
2. Скопируйте ffmpeg.exe и ffprobe.exe в папку проекта
3. Добавьте их в скрипт установщика

## Оптимизация размера

Для уменьшения размера .exe:

```bash
# Используйте UPX сжатие
pyinstaller --onefile --windowed --upx-dir=upx src/gui.py

# Или исключите ненужные модули
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module PIL.ImageTk src/gui.py
```

## Проверка готового установщика

1. Протестируйте на чистой системе (VM)
2. Убедитесь, что все зависимости включены
3. Проверьте работу без установленного Python
4. Протестируйте установку и удаление

## Распространение

Готовый установщик можно распространять через:
- GitHub Releases
- Google Drive / Dropbox
- Torrent-трекеры
- Собственный сайт
