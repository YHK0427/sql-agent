# database/init_history.py

import sqlite3
import os

DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DB = os.path.join(DATABASE_DIR, 'query_history.db')

def init_history_db():
    """쿼리 히스토리 저장용 DB 초기화"""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_name TEXT NOT NULL,
            question TEXT NOT NULL,
            sql_query TEXT NOT NULL,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_bookmarked INTEGER DEFAULT 0,
            result_rows INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ query_history.db 생성 완료")

if __name__ == '__main__':
    init_history_db()