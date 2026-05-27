import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            username TEXT,
            searches_count INTEGER DEFAULT 0,
            search_limits INTEGER DEFAULT 2,
            stars_balance INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mirrors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            bot_name TEXT,
            users_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Активно'
        )
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (tg_id, username, searches_count, search_limits, stars_balance)
        VALUES (874920472, 'user_tg', 42, 2, 0)
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO mirrors (creator_id, bot_name, users_count, status)
        VALUES (874920472, 'flagon_bot_v1', 142, 'Активно')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO mirrors (creator_id, bot_name, users_count, status)
        VALUES (874920472, 'shadow_probe_bot', 39, 'Активно')
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
