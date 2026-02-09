import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker # pip install faker 필요

# 한국어 더미 데이터 생성을 위한 Faker 설정
fake = Faker('ko_KR')

DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DB 저장 폴더가 없으면 생성
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

def create_ecommerce_db():
    """전자상거래 DB 생성 (대용량)"""
    db_path = os.path.join(DATABASE_DIR, 'ecommerce.db')
    if os.path.exists(db_path):
        os.remove(db_path) # 기존 파일 삭제 후 재생성

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 테이블 생성
    cursor.execute('''
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            tier TEXT CHECK(tier IN ('VIP', 'Basic', 'Gold', 'Silver')) DEFAULT 'Basic',
            join_date DATE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date DATETIME NOT NULL,
            status TEXT DEFAULT 'Completed',
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')
    
    print("🛒 전자상거래 데이터 생성 중...")

    # 2. Users 데이터 생성 (1,000명)
    users = []
    tiers = ['Basic', 'Basic', 'Basic', 'Silver', 'Silver', 'Gold', 'VIP'] # 비율 조정
    for _ in range(1000):
        users.append((
            fake.name(),
            fake.email(),
            random.choice(tiers),
            fake.date_between(start_date='-2y', end_date='today')
        ))
    cursor.executemany('INSERT INTO Users (name, email, tier, join_date) VALUES (?, ?, ?, ?)', users)
    print(f"   - 유저 1,000명 생성 완료")

    # 3. Products 데이터 생성 (50개)
    categories = {
        '전자제품': ['노트북', '스마트폰', '태블릿', '모니터', '마우스', '키보드', '헤드셋', '스마트워치', '충전기', 'USB허브'],
        '가구': ['게이밍 의자', '사무용 책상', '책장', '침대 프레임', '소파', '식탁', '조명', '서랍장'],
        '의류': ['티셔츠', '청바지', '후드티', '패딩', '양말 세트', '운동화', '슬랙스'],
        '식품': ['생수 2L', '라면 1BOX', '햇반', '커피 원두', '비타민', '단백질 보충제'],
        '도서': ['파이썬 코딩', 'SQL 정석', '인공지능 개론', '소설', '에세이']
    }
    
    products = []
    for cat, items in categories.items():
        for item in items:
            # 가격을 현실적으로 랜덤 생성 (천원 단위)
            price = random.randint(10, 3000) * 1000 
            if cat == '전자제품' or cat == '가구':
                price *= random.randint(2, 10) # 비싼 물건은 더 비싸게
            
            # 제품명 조금씩 변형 (예: 고급 게이밍 의자 A)
            product_name = f"{random.choice(['고급', '보급형', '신형', '가성비', ''])} {item} {random.choice(['A', 'B', 'Pro', 'Max', ''])}".strip()
            products.append((product_name, cat, price))
            
    cursor.executemany('INSERT INTO Products (product_name, category, price) VALUES (?, ?, ?)', products)
    print(f"   - 상품 {len(products)}개 생성 완료")

    # 4. Orders 데이터 생성 (20,000건)
    orders = []
    user_count = len(users)
    product_count = len(products)
    
    for _ in range(20000):
        user_id = random.randint(1, user_count)
        product_id = random.randint(1, product_count)
        quantity = random.choices([1, 2, 3, 4, 5, 10], weights=[70, 15, 5, 5, 3, 2])[0]
        
        # 주문 날짜: 최근 1년 이내 랜덤
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        status = random.choices(['Completed', 'Pending', 'Cancelled', 'Returned'], weights=[85, 5, 5, 5])[0]
        
        orders.append((user_id, product_id, quantity, order_date, status))
        
    cursor.executemany('INSERT INTO Orders (user_id, product_id, quantity, order_date, status) VALUES (?, ?, ?, ?, ?)', orders)
    print(f"   - 주문 20,000건 생성 완료")

    conn.commit()
    conn.close()

def create_hr_db():
    """인사관리 DB 생성 (대용량)"""
    db_path = os.path.join(DATABASE_DIR, 'hr_management.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE Departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL UNIQUE,
            location TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE Employees (
            emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dept_id INTEGER NOT NULL,
            position TEXT NOT NULL,
            salary INTEGER NOT NULL,
            hire_date DATE NOT NULL,
            email TEXT,
            FOREIGN KEY (dept_id) REFERENCES Departments(dept_id)
        )
    ''')
    
    print("👥 인사관리 데이터 생성 중...")
    
    # 1. 부서 생성
    dept_names = ['개발팀', '기획팀', '디자인팀', '마케팅팀', '인사팀', '재무팀', '영업팀', 'CS팀']
    depts = [(name, fake.city()) for name in dept_names]
    cursor.executemany('INSERT INTO Departments (dept_name, location) VALUES (?, ?)', depts)
    
    # 2. 직원 생성 (300명)
    employees = []
    positions = ['사원', '대리', '과장', '차장', '부장']
    base_salary = {'사원': 3500, '대리': 4500, '과장': 5500, '차장': 7000, '부장': 9000}
    
    for _ in range(300):
        dept_id = random.randint(1, len(dept_names))
        position = random.choices(positions, weights=[40, 30, 15, 10, 5])[0]
        
        # 급여: 직급별 기본급 + 랜덤 알파 (만원 단위)
        salary = (base_salary[position] + random.randint(-200, 500)) * 10000 
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        name = fake.name()
        email = fake.email()
        
        employees.append((name, dept_id, position, salary, hire_date, email))
        
    cursor.executemany('INSERT INTO Employees (name, dept_id, position, salary, hire_date, email) VALUES (?, ?, ?, ?, ?, ?)', employees)
    print(f"   - 직원 300명 생성 완료")

    conn.commit()
    conn.close()

def create_finance_db():
    """재무 DB 생성 (대용량)"""
    db_path = os.path.join(DATABASE_DIR, 'finance.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE Accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            account_type TEXT CHECK(account_type IN ('Revenue', 'Expense', 'Asset', 'Liability')) NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_date DATE NOT NULL,
            description TEXT,
            vendor TEXT,
            FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
        )
    ''')
    
    print("💰 재무 데이터 생성 중...")
    
    # 1. 계정 과목 생성
    accounts_data = [
        ('제품 매출', 'Revenue'), ('서비스 수익', 'Revenue'),
        ('급여', 'Expense'), ('임차료', 'Expense'), ('복리후생비', 'Expense'), ('광고선전비', 'Expense'), ('서버유지비', 'Expense'),
        ('법인카드 결제', 'Liability'), ('현금', 'Asset')
    ]
    cursor.executemany('INSERT INTO Accounts (account_name, account_type) VALUES (?, ?)', accounts_data)
    
    # 2. 거래 내역 생성 (10,000건)
    transactions = []
    account_count = len(accounts_data)
    
    for _ in range(10000):
        account_idx = random.randint(0, account_count - 1)
        acc_name, acc_type = accounts_data[account_idx]
        
        # 금액: Revenue는 + 크기, Expense는 작지만 빈번하게
        if acc_type == 'Revenue':
            amount = random.randint(10, 1000) * 100000 # 100만 ~ 1억
            desc = f"계약금_{fake.company()}"
        else:
            amount = random.randint(1, 500) * 10000 # 1만 ~ 500만
            desc = f"{acc_name} 지출"
            
        trans_date = fake.date_between(start_date='-1y', end_date='today')
        vendor = fake.company()
        
        transactions.append((account_idx + 1, amount, trans_date, desc, vendor))
        
    cursor.executemany('INSERT INTO Transactions (account_id, amount, transaction_date, description, vendor) VALUES (?, ?, ?, ?, ?)', transactions)
    print(f"   - 거래 내역 10,000건 생성 완료")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    print(f"🚀 대용량 샘플 데이터베이스 생성을 시작합니다...")
    create_ecommerce_db()
    create_hr_db()
    create_finance_db()
    print("\n🎉 모든 DB 생성 완료! (faker 라이브러리 사용됨)")