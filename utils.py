# utils.py
# Здесь будут функции для скачивания, конвертации и прогресса

import yt_dlp
import os
import uuid

def download_video(url, quality, filetype, progress_callback=None):
    filename = f"video_{uuid.uuid4().hex}.{filetype}"
    
    # Настройки yt-dlp
    ydl_opts = {
        'format': f'best[height<={quality[:-1]}][ext={filetype}]/best[ext={filetype}]/best',
        'outtmpl': filename,
        'noplaylist': True,
    }
    
    if progress_callback:
        def hook(d):
            if d['status'] == 'downloading':
                if 'downloaded_bytes' in d and 'total_bytes' in d:
                    percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
                    progress_callback(percent)
            elif d['status'] == 'finished':
                progress_callback(100)
        ydl_opts['progress_hooks'] = [hook]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        return filename, filesize
    else:
        raise Exception('Файл не был загружен')

def extract_audio(url, progress_callback=None):
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': filename.replace('.mp3', '.%(ext)s'),
        'noplaylist': True,
    }
    
    if progress_callback:
        def hook(d):
            if d['status'] == 'downloading':
                if 'downloaded_bytes' in d and 'total_bytes' in d:
                    percent = int(d['downloaded_bytes'] / d['total_bytes'] * 80)  # 80% на загрузку
                    progress_callback(percent)
            elif d['status'] == 'finished':
                progress_callback(85)  # 85% после загрузки
            elif d['status'] == 'postprocess':
                progress_callback(95)  # 95% во время конвертации
        ydl_opts['progress_hooks'] = [hook]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    if progress_callback:
        progress_callback(100)
    
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        return filename, filesize
    else:
        raise Exception('Аудиофайл не был создан')

def get_video_info(url):
    """Получает информацию о видео для формирования кнопок выбора качества"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
    # Получаем доступные форматы
    formats = info.get('formats', [])
    
    # Фильтруем качества видео
    video_qualities = set()
    for fmt in formats:
        if fmt.get('vcodec') != 'none' and fmt.get('height'):
            height = fmt['height']
            if height >= 144:  # Минимальное качество
                if height <= 240:
                    video_qualities.add('144p')
                elif height <= 360:
                    video_qualities.add('360p')
                elif height <= 480:
                    video_qualities.add('480p')
                elif height <= 720:
                    video_qualities.add('720p')
                elif height <= 1080:
                    video_qualities.add('1080p')
                elif height <= 2160:
                    video_qualities.add('2160p')
    
    # Проверяем доступность аудио
    has_audio = any(fmt.get('acodec') != 'none' for fmt in formats)
    
    return {
        'title': info.get('title', 'Unknown'),
        'video_qualities': sorted(video_qualities, key=lambda x: int(x[:-1]), reverse=True),
        'has_audio': has_audio
    } 