import sqlite3
from pathlib import Path

# Връзка към базата данни
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print("DB Connection Error:", e)
        return None

# --- Основно изпълнение на SQL команди за една заявка ---
def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print("SQL Error:", e)
        conn.close()
        return None

# --- За изпълнение на множество SQL команди наведнъж ---
def execute_script(script):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.executescript(script)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print("SQL Script Error:", e)
        conn.close()
        return None