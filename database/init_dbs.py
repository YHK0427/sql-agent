# database/init_dbs.py

import sqlite3
import os
from datetime import datetime, timedelta
import random

DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_ecommerce_db():
    """전자상거래 DB 생성"""
    db_path = os.path.join(DATABASE_DIR, 'ecommerce.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tier TEXT CHECK(tier IN ('VIP', 'Basic')) DEFAULT 'Basic',
            join_date DATE NOT NULL
        )
    ''')
    
    # Products 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    # Orders 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')
    
    # 샘플 데이터 삽입
    users = [
        ('김철수', 'VIP', '2023-01-15'),
        ('이영희', 'Basic', '2023-03-22'),
        ('박민수', 'VIP', '2023-05-10'),
        ('정수진', 'Basic', '2023-07-08'),
        ('최동욱', 'VIP', '2023-09-12')
    ]
    cursor.executemany('INSERT INTO Users (name, tier, join_date) VALUES (?, ?, ?)', users)
    
    products = [
        ('노트북', '전자제품', 1200000),
        ('마우스', '전자제품', 35000),
        ('키보드', '전자제품', 89000),
        ('모니터', '전자제품', 350000),
        ('책상', '가구', 150000)
    ]
    cursor.executemany('INSERT INTO Products (product_name, category, price) VALUES (?, ?, ?)', products)
    
    # 주문 데이터 (랜덤 생성)
    for _ in range(20):
        user_id = random.randint(1, 5)
        product_id = random.randint(1, 5)
        quantity = random.randint(1, 3)
        days_ago = random.randint(1, 90)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO Orders (user_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)',
                      (user_id, product_id, quantity, order_date))
    
    conn.commit()
    conn.close()
    print(f"✅ ecommerce.db 생성 완료")

def create_hr_db():
    """인사관리 DB 생성"""
    db_path = os.path.join(DATABASE_DIR, 'hr_management.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Departments 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Employees 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dept_id INTEGER NOT NULL,
            salary REAL NOT NULL,
            hire_date DATE NOT NULL,
            FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
        )
    ''')
    
    # 샘플 데이터
    departments = [('개발팀',), ('마케팅팀',), ('인사팀',), ('영업팀',)]
    cursor.executemany('INSERT INTO Departments (dept_name) VALUES (?)', departments)
    
    employees = [
        ('홍길동', 1, 5000000, '2020-03-01'),
        ('김영수', 1, 5500000, '2019-06-15'),
        ('이지은', 2, 4200000, '2021-01-10'),
        ('박서준', 3, 4000000, '2021-08-20'),
        ('최민호', 4, 4800000, '2020-11-05')
    ]
    cursor.executemany('INSERT INTO Employees (name, dept_id, salary, hire_date) VALUES (?, ?, ?, ?)', employees)
    
    conn.commit()
    conn.close()
    print(f"✅ hr_management.db 생성 완료")

def create_finance_db():
    """재무 DB 생성"""
    db_path = os.path.join(DATABASE_DIR, 'finance.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Accounts 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            account_type TEXT CHECK(account_type IN ('수익', '비용')) NOT NULL
        )
    ''')
    
    # Transactions 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_date DATE NOT NULL,
            description TEXT,
            FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
        )
    ''')
    
    # 샘플 데이터
    accounts = [
        ('매출', '수익'),
        ('인건비', '비용'),
        ('광고비', '비용'),
        ('임대료', '비용')
    ]
    cursor.executemany('INSERT INTO Accounts (account_name, account_type) VALUES (?, ?)', accounts)
    
    # 거래 내역 (랜덤)
    for _ in range(30):
        account_id = random.randint(1, 4)
        amount = random.randint(100000, 5000000)
        days_ago = random.randint(1, 180)
        transaction_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO Transactions (account_id, amount, transaction_date, description) VALUES (?, ?, ?, ?)',
                      (account_id, amount, transaction_date, f'거래_{_+1}'))
    
    conn.commit()
    conn.close()
    print(f"✅ finance.db 생성 완료")

if __name__ == '__main__':
    print("샘플 데이터베이스 생성 중...")
    create_ecommerce_db()
    create_hr_db()
    create_finance_db()
    print("\n🎉 모든 DB 생성 완료!")