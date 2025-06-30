# YouTube Video Downloader Bot

Telegram-бот для скачивания видео с YouTube в различных форматах и качестве.

## 🚀 Возможности

- **Поддержка разрешений**: 144p, 360p, 480p, 720p, 1080p, 2160p (4K)
- **Форматы**: MP4, WebM, MP3 (аудио)
- **Локализация**: русский и английский языки
- **Прогресс загрузки**: отображение процента скачивания
- **Кэширование**: повторная отправка файлов без перезагрузки
- **Автоочистка**: удаление старых файлов

## 📋 Требования

- Python 3.10+
- FFmpeg (для конвертации аудио)
- Telegram Bot Token от @BotFather

## 🛠 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/youtubevideodownloader.git
cd youtubevideodownloader
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Установка FFmpeg

**Windows:**
- Скачайте с [ffmpeg.org](https://ffmpeg.org/download.html)
- Добавьте в PATH

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

### 4. Настройка

Отредактируйте файл `config.py`:
```python
TELEGRAM_TOKEN = "ваш_токен_от_BotFather"
MAX_FILE_SIZE = 2000  # МБ (лимит Telegram)
LANGUAGES = ['ru', 'en']
```

### 5. Запуск
```bash
python bot.py
```

## 🖥 Деплой на сервер

### Ubuntu/Debian сервер

1. **Обновление системы:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установка Python и FFmpeg:**
```bash
sudo apt install python3 python3-pip ffmpeg git -y
```

3. **Клонирование и установка:**
```bash
git clone https://github.com/your-username/youtubevideodownloader.git
cd youtubevideodownloader
pip3 install -r requirements.txt
```

4. **Настройка автозапуска (systemd):**

Создайте файл `/etc/systemd/system/ytbot.service`:
```ini
[Unit]
Description=YouTube Downloader Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/youtubevideodownloader
ExecStart=/usr/bin/python3 /path/to/youtubevideodownloader/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ytbot
sudo systemctl start ytbot
sudo systemctl status ytbot
```

## 🐳 Docker (опционально)

1. **Создание Dockerfile:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

2. **Сборка и запуск:**
```bash
docker build -t ytbot .
docker run -d --name youtube-bot --restart unless-stopped ytbot
```

## 🚀 Развёртывание на Render.com

1. **Форкните или загрузите проект на GitHub.**
2. **Создайте сервис на Render.com:**
   - Зайдите на https://dashboard.render.com и выберите "New Web Service".
   - Подключите ваш репозиторий.
   - В настройках выберите:
     - Environment: **Python 3.11**
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python bot.py`
   - В разделе "Environment" добавьте переменные:
     - `TELEGRAM_TOKEN` — ваш токен Telegram-бота
     - (опционально) другие переменные из config.py
3. **FFmpeg:**
   - Render поддерживает установку пакетов через Apt. В настройках добавьте файл `render.yaml` (см. ниже).

### Пример файла render.yaml
```yaml
services:
  - type: web
    name: youtubevideodownloader
    env: python
    buildCommand: "apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt"
    startCommand: "python bot.py"
    envVars:
      - key: TELEGRAM_TOKEN
        value: <ваш_токен>
```

4. **Загрузите файл `render.yaml` в корень проекта.**
5. **Деплойте!** После деплоя бот будет работать автоматически.

## 📱 Использование

1. Найдите бота в Telegram по имени или ссылке
2. Отправьте команду `/start`
3. Выберите язык командой `/lang`
4. Отправьте ссылку на YouTube видео
5. Выберите желаемое качество и формат
6. Дождитесь скачивания и получите файл

## 🛡 Безопасность

- Соблюдает YouTube Terms of Service
- Автоматическая очистка временных файлов
- Ограничение размера файлов (2 ГБ)
- Кэширование для оптимизации

## 📝 Команды бота

- `/start` — приветствие и инструкция
- `/help` — справка по использованию  
- `/lang` — смена языка (русский/английский)

## 🔧 Конфигурация

Все настройки находятся в файле `config.py`:

- `TELEGRAM_TOKEN` — токен бота от @BotFather
- `MAX_FILE_SIZE` — максимальный размер файла в МБ
- `LANGUAGES` — поддерживаемые языки

## 🐛 Решение проблем

**Ошибка "HTTP Error 400":**
- Убедитесь, что используется последняя версия yt-dlp
- Проверьте доступность видео

**Ошибка конвертации аудио:**
- Установите FFmpeg
- Проверьте PATH для FFmpeg

**Конфликт экземпляров бота:**
- Убедитесь, что запущен только один экземпляр
- Проверьте процессы: `ps aux | grep python`

## 📄 Лицензия

MIT License

## 🤝 Поддержка

При возникновении проблем создайте Issue в репозитории. 