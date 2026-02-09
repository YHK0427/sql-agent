# utils/query_generator.py

import re
from utils.gemini_client import ask_gemini
from utils.schema_analyzer import get_database_schema

def generate_sql_from_question(db_path, user_question):
    """
    자연어 질문을 SQL 쿼리로 변환
    
    Args:
        db_path: DB 파일 경로
        user_question: 사용자의 자연어 질문
    
    Returns:
        dict: {
            'reasoning': 'AI의 사고 과정',
            'sql': '생성된 SQL 쿼리'
        }
    """
    schema_info = get_database_schema(db_path)
    
    prompt = f"""
당신은 SQLite 전문가입니다. 사용자의 질문을 SQL 쿼리로 변환해주세요.

<데이터베이스 스키마>
{schema_info['schema_text']}

<사용자 질문>
{user_question}

응답 형식을 **반드시** 아래와 같이 작성하세요:

<reasoning>
사용자가 원하는 것을 어떻게 해석했는지, 어떤 테이블과 컬럼을 사용할지 설명
</reasoning>

<sql>
SELECT ...
FROM ...
</sql>

주의사항:
- 스키마에 없는 테이블이나 컬럼은 절대 사용하지 마세요
- SQL은 실행 가능한 완전한 쿼리여야 합니다
- SQLite 문법을 사용하세요
"""
    
    response = ask_gemini(prompt)
    
    # reasoning과 sql 파싱
    reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response, re.DOTALL)
    sql_match = re.search(r'<sql>(.*?)</sql>', response, re.DOTALL)
    
    reasoning = reasoning_match.group(1).strip() if reasoning_match else "분석 중..."
    sql = sql_match.group(1).strip() if sql_match else "-- SQL 생성 실패"
    
    return {
        'reasoning': reasoning,
        'sql': sql
    }

def execute_sql(db_path, sql_query):
    """
    SQL 쿼리를 실행하고 결과 반환
    
    Returns:
        dict: {
            'success': bool,
            'columns': [컬럼명 리스트],
            'rows': [데이터 행들],
            'error': 에러 메시지 (실패 시)
        }
    """
    import sqlite3
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        
        # 컬럼명 추출
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # 데이터 fetch
        rows = cursor.fetchall()
        
        conn.close()
        
        return {
            'success': True,
            'columns': columns,
            'rows': rows
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
def save_to_history(db_name, question, sql_query, result_rows=0):
    """
    쿼리 히스토리 저장
    
    Args:
        db_name: DB 이름
        question: 사용자 질문
        sql_query: 생성된 SQL
        result_rows: 결과 행 개수
    """
    from config import HISTORY_DB
    import sqlite3
    
    try:
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_history (db_name, question, sql_query, result_rows)
            VALUES (?, ?, ?, ?)
        ''', (db_name, question, sql_query, result_rows))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"히스토리 저장 실패: {e}")
        return False

def get_history(db_name=None, limit=50):
    """
    쿼리 히스토리 조회
    
    Args:
        db_name: 특정 DB만 필터 (None이면 전체)
        limit: 최대 개수
    
    Returns:
        list: 히스토리 리스트
    """
    from config import HISTORY_DB
    import sqlite3
    
    try:
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        
        if db_name:
            cursor.execute('''
                SELECT id, db_name, question, sql_query, executed_at, is_bookmarked, result_rows
                FROM query_history
                WHERE db_name = ?
                ORDER BY executed_at DESC
                LIMIT ?
            ''', (db_name, limit))
        else:
            cursor.execute('''
                SELECT id, db_name, question, sql_query, executed_at, is_bookmarked, result_rows
                FROM query_history
                ORDER BY executed_at DESC
                LIMIT ?
            ''', (limit,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'db_name': row[1],
                'question': row[2],
                'sql_query': row[3],
                'executed_at': row[4],
                'is_bookmarked': row[5],
                'result_rows': row[6]
            }
            for row in history
        ]
    except Exception as e:
        print(f"히스토리 조회 실패: {e}")
        return []

def toggle_bookmark(history_id):
    """북마크 토글"""
    from config import HISTORY_DB
    import sqlite3
    
    try:
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE query_history
            SET is_bookmarked = CASE WHEN is_bookmarked = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        ''', (history_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"북마크 토글 실패: {e}")
        return False