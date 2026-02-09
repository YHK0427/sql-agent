# utils/schema_analyzer.py

import sqlite3
from utils.gemini_client import ask_gemini

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

def analyze_schema_with_llm(db_path):
    """
    LLM을 사용해 DB 스키마를 분석하고 설명 생성
    
    Returns:
        str: DB 구조에 대한 자연어 설명
    """
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
    
    analysis = ask_gemini(prompt)
    return analysis

def suggest_queries_with_llm(db_path):
    """
    LLM을 사용해 이 DB에서 할 수 있는 유용한 질문 예시 생성
    
    Returns:
        list: 추천 질문 리스트 (최대 5개)
    """
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
    
    response = ask_gemini(prompt)
    
    # 응답을 리스트로 파싱
    lines = response.strip().split('\n')
    queries = []
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # "1. " 또는 "- " 제거
            query = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('-').strip()
            queries.append(query)
    
    return queries[:5]  # 최대 5개

def generate_schema_diagram(db_path):
    """
    DB 스키마를 Mermaid ER 다이어그램으로 변환
    
    Returns:
        str: Mermaid 문법의 ER 다이어그램 코드
    """
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
    
    # FK 관계 추출 (PRAGMA foreign_key_list 사용)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for table_name in schema_info['tables']:
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        for fk in fks:
            # fk: (id, seq, table, from, to, on_update, on_delete, match)
            ref_table = fk[2]  # 참조 테이블
            from_col = fk[3]   # 현재 테이블의 FK 컬럼
            to_col = fk[4]     # 참조 테이블의 PK 컬럼
            
            # Mermaid 관계 표현: 현재테이블 ||--o{ 참조테이블 : "관계명"
            mermaid += f'    {ref_table} ||--o{{ {table_name} : "has"\n'
    
    conn.close()
    
    return mermaid