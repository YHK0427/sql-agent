# utils/schema_analyzer.py

import sqlite3
import json
import os
from datetime import datetime
from utils.gemini_client import ask_gemini

# 캐시 파일 경로
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
CACHE_FILE = os.path.join(CACHE_DIR, 'schema_cache.json')

def _load_cache():
    """캐시 파일 로드"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache(cache):
    """캐시 파일 저장"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def _get_db_modified_time(db_path):
    """DB 파일 수정 시간"""
    return os.path.getmtime(db_path)

def get_database_schema(db_path):
    """
    SQLite DB의 전체 스키마 정보를 추출
    
    Returns:
        dict: {
            'tables': [테이블명 리스트],
            'schema_text': 'CREATE TABLE 구문들',
            'table_info': {테이블명: {columns: [...], sample_data: [...]}}
        }
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 모든 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 각 테이블의 CREATE 구문
    schema_text = ""
    table_info = {}
    
    for table in tables:
        # CREATE TABLE 구문
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_stmt = cursor.fetchone()[0]
        schema_text += f"{create_stmt};\n\n"
        
        # 컬럼 정보
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # 샘플 데이터 (최대 3개)
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_data = cursor.fetchall()
        
        table_info[table] = {
            'columns': columns,
            'sample_data': sample_data
        }
    
    conn.close()
    
    return {
        'tables': tables,
        'schema_text': schema_text,
        'table_info': table_info
    }

def analyze_schema_with_llm(db_path, model_name='gemini-2.0-flash'):
    """
    LLM을 사용해 DB 스키마를 분석하고 설명 생성 (캐싱 적용)
    
    Returns:
        str: DB 구조에 대한 자연어 설명
    """
    # 캐시 로드
    cache = _load_cache()
    db_name = os.path.basename(db_path)
    db_mtime = _get_db_modified_time(db_path)
    
    # 캐시 확인
    if db_name in cache:
        cached_data = cache[db_name]
        # DB 파일이 수정되지 않았고, 같은 모델이면 캐시 사용
        if cached_data.get('mtime') == db_mtime and cached_data.get('model') == model_name:
            print(f"[CACHE HIT] {db_name} 스키마 분석 캐시 사용")
            return cached_data['analysis']
    
    # 캐시 미스 - LLM 호출
    print(f"[CACHE MISS] {db_name} 스키마 분석 중... (LLM 호출)")
    schema_info = get_database_schema(db_path)
    
    prompt = f"""
당신은 데이터베이스 전문가입니다. 아래 SQLite 데이터베이스의 구조를 분석하고 사용자가 이해하기 쉽게 설명해주세요.

<데이터베이스 스키마>
{schema_info['schema_text']}

다음 형식으로 설명해주세요:
1. 이 데이터베이스가 다루는 도메인/주제
2. 각 테이블의 역할 (2-3문장으로 간단히)
3. 테이블 간 관계 (FK가 있다면)

간결하고 명확하게 작성해주세요.
"""
    
    analysis = ask_gemini(prompt, model_name=model_name)
    
    # 캐시 저장
    cache[db_name] = {
        'analysis': analysis,
        'mtime': db_mtime,
        'model': model_name,
        'cached_at': datetime.now().isoformat()
    }
    _save_cache(cache)
    
    return analysis

def suggest_queries_with_llm(db_path, model_name='gemini-2.0-flash'):
    """
    LLM을 사용해 이 DB에서 할 수 있는 유용한 질문 예시 생성 (캐싱 적용)
    
    Returns:
        list: 추천 질문 리스트 (최대 5개)
    """
    # 캐시 로드
    cache = _load_cache()
    db_name = os.path.basename(db_path)
    db_mtime = _get_db_modified_time(db_path)
    
    # 캐시 확인
    cache_key = f"{db_name}_queries"
    if cache_key in cache:
        cached_data = cache[cache_key]
        if cached_data.get('mtime') == db_mtime and cached_data.get('model') == model_name:
            print(f"[CACHE HIT] {db_name} 추천 질문 캐시 사용")
            return cached_data['queries']
    
    # 캐시 미스 - LLM 호출
    print(f"[CACHE MISS] {db_name} 추천 질문 생성 중... (LLM 호출)")
    schema_info = get_database_schema(db_path)
    
    prompt = f"""
당신은 데이터 분석가입니다. 아래 데이터베이스를 보고, 사용자가 물어볼 만한 **유용하고 구체적인 질문 5개**를 제안해주세요.

<데이터베이스 스키마>
{schema_info['schema_text']}

조건:
- 실제 비즈니스 인사이트를 얻을 수 있는 질문
- JOIN이 필요한 질문 포함
- 집계 함수(SUM, COUNT, AVG 등)를 사용하는 질문 포함

형식:
1. 질문1
2. 질문2
3. 질문3
4. 질문4
5. 질문5

번호와 질문만 작성하고, 추가 설명은 불필요합니다.
"""
    
    response = ask_gemini(prompt, model_name=model_name)
    
    # 응답을 리스트로 파싱
    lines = response.strip().split('\n')
    queries = []
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # "1. " 또는 "- " 제거
            query = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('-').strip()
            queries.append(query)
    
    queries = queries[:5]  # 최대 5개
    
    # 캐시 저장
    cache[cache_key] = {
        'queries': queries,
        'mtime': db_mtime,
        'model': model_name,
        'cached_at': datetime.now().isoformat()
    }
    _save_cache(cache)
    
    return queries

def generate_schema_diagram(db_path):
    """
    DB 스키마를 Mermaid ER 다이어그램으로 변환 (캐싱 적용)
    
    Returns:
        str: Mermaid 문법의 ER 다이어그램 코드
    """
    # 캐시 로드
    cache = _load_cache()
    db_name = os.path.basename(db_path)
    db_mtime = _get_db_modified_time(db_path)
    
    # 캐시 확인
    cache_key = f"{db_name}_diagram"
    if cache_key in cache:
        cached_data = cache[cache_key]
        if cached_data.get('mtime') == db_mtime:
            print(f"[CACHE HIT] {db_name} 다이어그램 캐시 사용")
            return cached_data['diagram']
    
    # 캐시 미스 - 다이어그램 생성
    print(f"[CACHE MISS] {db_name} 다이어그램 생성 중...")
    schema_info = get_database_schema(db_path)
    
    mermaid = "erDiagram\n"
    
    # 각 테이블의 컬럼 정의
    for table_name, table_data in schema_info['table_info'].items():
        columns = table_data['columns']
        
        # 테이블 정의
        mermaid += f"    {table_name} {{\n"
        for col in columns:
            col_id = col[0]  # column id
            col_name = col[1]  # column name
            col_type = col[2]  # data type
            is_pk = col[5]  # primary key (1 or 0)
            
            # PK 표시
            pk_marker = "PK" if is_pk else ""
            mermaid += f"        {col_type} {col_name} {pk_marker}\n"
        
        mermaid += "    }\n"
    
    # FK 관계 추출
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for table_name in schema_info['tables']:
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        for fk in fks:
            ref_table = fk[2]  # 참조 테이블
            mermaid += f'    {ref_table} ||--o{{ {table_name} : "has"\n'
    
    conn.close()
    
    # 캐시 저장
    cache[cache_key] = {
        'diagram': mermaid,
        'mtime': db_mtime,
        'cached_at': datetime.now().isoformat()
    }
    _save_cache(cache)
    
    return mermaid

def clear_cache(db_name=None):
    """
    캐시 삭제 (DB 수정 시 수동 호출용)
    
    Args:
        db_name: 특정 DB만 삭제 (None이면 전체 삭제)
    """
    cache = _load_cache()
    
    if db_name:
        # 특정 DB 캐시만 삭제
        keys_to_delete = [k for k in cache.keys() if k.startswith(db_name)]
        for key in keys_to_delete:
            del cache[key]
        print(f"[CACHE] {db_name} 캐시 삭제됨")
    else:
        # 전체 캐시 삭제
        cache = {}
        print("[CACHE] 전체 캐시 삭제됨")
    
    _save_cache(cache)