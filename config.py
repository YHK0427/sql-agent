# config.py

import os
import json

# 프로젝트 루트 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
METADATA_FILE = os.path.join(DATABASE_DIR, 'metadata.json')

def load_databases():
    """
    database/ 폴더의 .db 파일들을 스캔하고 metadata.json과 매핑
    """
    databases = {}
    
    # metadata.json 로드
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # .db 파일들 스캔
    for filename in os.listdir(DATABASE_DIR):
        if filename.endswith('.db'):
            db_key = filename.replace('.db', '')
            db_path = os.path.join(DATABASE_DIR, filename)
            
            # metadata가 있으면 사용, 없으면 기본값
            if db_key in metadata:
                databases[db_key] = {
                    'name': metadata[db_key]['name'],
                    'description': metadata[db_key]['description'],
                    'icon': metadata[db_key]['icon'],
                    'file': db_path
                }
            else:
                # metadata 없으면 기본값으로 추가
                databases[db_key] = {
                    'name': db_key.replace('_', ' ').title(),
                    'description': 'No description',
                    'icon': '📁',
                    'file': db_path
                }
    
    return databases

# 전역 변수로 사용
DATABASES = load_databases()