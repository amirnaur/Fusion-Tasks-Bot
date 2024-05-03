# database.py
import sqlite3

DATABASE_PATH = 'users.db'

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def setup_database():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                notion_user_id TEXT
            );
        ''')
        conn.commit()

def set_user_notion_id(user_id, notion_user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, notion_user_id) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET notion_user_id=excluded.notion_user_id;
        ''', (user_id, notion_user_id))
        conn.commit()

def get_user_notion_id(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT notion_user_id FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
    return result[0] if result else None


if __name__ == "__main__":
    setup_database()
    print("Database has been set up.")
