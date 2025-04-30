import sqlite3

def init_db():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_job(title, link):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jobs (title, link) VALUES (?, ?)", (title, link))
    conn.commit()
    conn.close()
