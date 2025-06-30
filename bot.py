import telebot
from telebot import types
from config import TELEGRAM_TOKEN, LANGUAGES, MAX_FILE_SIZE
import re
from utils import download_video, extract_audio, get_video_info
import os
import threading
from db import cache_request, get_cached, clear_old_cache
import time
import traceback

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_lang = {}

# Регулярка для проверки YouTube-ссылки
YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+')

# Словарь для хранения временных данных пользователя (например, доступные потоки)
user_video_data = {}

# Локализация (упрощённо)
LOCALES = {
    'ru': {
        'start': '👋 Привет! Я помогу скачать видео с YouTube. Просто пришли мне ссылку!\nИспользуй /help для справки.',
        'help': 'Отправь ссылку на YouTube-видео. После этого выбери нужное качество и формат. Максимальный размер файла — 2 ГБ.',
        'lang': 'Выберите язык:',
        'lang_set': 'Язык установлен: Русский 🇷🇺',
        'invalid_link': 'Ошибка: некорректная ссылка на YouTube.',
        'no_quality': 'Данное качество недоступно. Выберите из списка.',
        'download_fail': 'Сбой при скачивании. Попробуйте позже.',
        'analyze_fail': 'Сбой при анализе видео. Попробуйте позже.',
        'oversize': 'Ошибка: файл превышает лимит 2 ГБ.',
        'session_expired': 'Сессия устарела. Пришлите ссылку заново.',
        'choose_quality': 'Выберите качество и формат:',
        'downloading': 'Загрузка: {percent}%',
        'download_started': 'Загрузка началась...'
    },
    'en': {
        'start': '👋 Hi! I can help you download YouTube videos. Just send me a link!\nUse /help for more info.',
        'help': 'Send a YouTube video link. Then choose the desired quality and format. Max file size — 2 GB.',
        'lang': 'Choose language:',
        'lang_set': 'Language set: English 🇬🇧',
        'invalid_link': 'Error: invalid YouTube link.',
        'no_quality': 'This quality is not available. Please choose from the list.',
        'download_fail': 'Download failed. Please try again later.',
        'analyze_fail': 'Failed to analyze video. Please try again later.',
        'oversize': 'Error: file exceeds 2 GB limit.',
        'session_expired': 'Session expired. Please send the link again.',
        'choose_quality': 'Choose quality and format:',
        'downloading': 'Downloading: {percent}%',
        'download_started': 'Download started...'
    }
}

def get_locale(message):
    return user_lang.get(message.from_user.id, 'ru')

@bot.message_handler(commands=['start'])
def start_message(message):
    lang = get_locale(message)
    bot.send_message(message.chat.id, LOCALES[lang]['start'])

@bot.message_handler(commands=['help'])
def help_message(message):
    lang = get_locale(message)
    bot.send_message(message.chat.id, LOCALES[lang]['help'])

@bot.message_handler(commands=['lang'])
def lang_message(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Русский 🇷🇺', callback_data='lang_ru'))
    markup.add(types.InlineKeyboardButton('English 🇬🇧', callback_data='lang_en'))
    lang = get_locale(message)
    bot.send_message(message.chat.id, LOCALES[lang]['lang'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_lang(call):
    lang_code = call.data.split('_')[1]
    user_lang[call.from_user.id] = lang_code
    bot.answer_callback_query(call.id, LOCALES[lang_code]['lang_set'])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=LOCALES[lang_code]['lang_set'])

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_youtube_link(message):
    lang = get_locale(message)
    url = message.text.strip()
    if not YOUTUBE_REGEX.match(url):
        bot.send_message(message.chat.id, LOCALES[lang]['invalid_link'])
        return
    try:
        video_info = get_video_info(url)
        qualities = video_info['video_qualities']
        has_audio = video_info['has_audio']
        
        if not qualities and not has_audio:
            bot.send_message(message.chat.id, LOCALES[lang]['no_quality'])
            return
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        
        # Добавляем кнопки для видео MP4
        for quality in qualities:
            buttons.append(types.InlineKeyboardButton(f'{quality} MP4', callback_data=f'video_{quality}_mp4'))
        
        # Добавляем кнопки для видео WebM (упрощенно - yt-dlp сам выберет лучший формат)
        for quality in qualities[:3]:  # Только топ-3 качества для WebM
            buttons.append(types.InlineKeyboardButton(f'{quality} WebM', callback_data=f'video_{quality}_webm'))
        
        # Аудио
        if has_audio:
            buttons.append(types.InlineKeyboardButton('MP3 (аудио)', callback_data='audio_mp3'))
        
        markup.add(*buttons)
        user_video_data[message.from_user.id] = {'url': url}
        bot.send_message(message.chat.id, LOCALES[lang]['choose_quality'], reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, LOCALES[lang]['analyze_fail'])

def send_progress(chat_id, msg_id, percent, lang):
    try:
        bot.edit_message_text(LOCALES[lang]['downloading'].format(percent=percent), chat_id, msg_id)
    except:
        pass

def download_and_send(user_id, chat_id, url, choice, message_id, lang):
    filename = None
    cache_key = f'{choice}'
    # Проверка кэша
    cached = get_cached(user_id, url + cache_key)
    if cached and os.path.exists(cached):
        try:
            bot.edit_message_text(LOCALES[lang]['downloading'].format(percent=100), chat_id, message_id)
            with open(cached, 'rb') as f:
                bot.send_document(chat_id, f, visible_file_name=os.path.basename(cached))
            return
        except Exception as e:
            print('Ошибка при отправке кэшированного файла:', e)
    try:
        if choice.startswith('video_'):
            _, res, ext = choice.split('_')
            filename, filesize = download_video(url, res, ext, lambda p: send_progress(chat_id, message_id, p, lang))
        elif choice == 'audio_mp3':
            filename, filesize = extract_audio(url, lambda p: send_progress(chat_id, message_id, p, lang))
        else:
            bot.send_message(chat_id, LOCALES[lang]['no_quality'])
            return
        if filesize > MAX_FILE_SIZE * 1024 * 1024:
            bot.send_message(chat_id, LOCALES[lang]['oversize'])
            os.remove(filename)
            return
        with open(filename, 'rb') as f:
            bot.send_document(chat_id, f, visible_file_name=os.path.basename(filename))
        # Сохраняем путь к файлу в кэш (на 1 час)
        cache_request(user_id, url + cache_key, filename)
        # Если кэш не используется, удаляем файл после отправки
        os.remove(filename)
    except Exception as e:
        print(e)
        bot.send_message(chat_id, LOCALES[lang]['download_fail'])
        try:
            if filename and os.path.exists(filename):
                os.remove(filename)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('video_') or call.data == 'audio_mp3')
def handle_quality_choice(call):
    user_id = call.from_user.id
    lang = get_locale(call)
    data = user_video_data.get(user_id)
    if not data:
        bot.answer_callback_query(call.id, LOCALES[lang]['session_expired'])
        return
    url = data['url']
    choice = call.data
    msg = bot.send_message(call.message.chat.id, LOCALES[lang]['downloading'].format(percent=0))
    bot.answer_callback_query(call.id, LOCALES[lang]['download_started'])
    threading.Thread(target=download_and_send, args=(user_id, call.message.chat.id, url, choice, msg.message_id, lang)).start()

def clear_cache_files_and_db():
    while True:
        clear_old_cache(86400)  # 1 день
        # Удаляем устаревшие файлы из кэша
        from db import conn
        c = conn.cursor()
        ts = int(time.time())
        c.execute('SELECT result, timestamp FROM cache')
        for row in c.fetchall():
            filename, file_ts = row
            if ts - file_ts > 86400 and filename and os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception as e:
                    print('Ошибка при удалении файла из кэша:', e)
        time.sleep(3600)  # Проверять каждый час

# Запуск фоновой очистки
threading.Thread(target=clear_cache_files_and_db, daemon=True).start()

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True) 