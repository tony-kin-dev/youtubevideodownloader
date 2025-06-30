import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2000))  # МБ
LANGUAGES = os.getenv("LANGUAGES", "ru,en").split(",")
