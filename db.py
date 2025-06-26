# db.py
# Здесь будет кэширование запросов (SQLite или Redis)

import sqlite3
import time

DB_PATH = 'cache.db'

# Инициализация базы
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS cache (
    user_id INTEGER,
    url TEXT,
    result TEXT,
    timestamp INTEGER
)''')
conn.commit()

def cache_request(user_id, url, result):
    ts = int(time.time())
    c.execute('INSERT INTO cache (user_id, url, result, timestamp) VALUES (?, ?, ?, ?)', (user_id, url, result, ts))
    conn.commit()

def get_cached(user_id, url, max_age=3600):
    ts = int(time.time())
    c.execute('SELECT result, timestamp FROM cache WHERE user_id=? AND url=? ORDER BY timestamp DESC LIMIT 1', (user_id, url))
    row = c.fetchone()
    if row and ts - row[1] < max_age:
        return row[0]
    return None

def clear_old_cache(max_age=86400):
    ts = int(time.time())
    c.execute('DELETE FROM cache WHERE ? - timestamp > ?', (ts, max_age))
    conn.commit() 