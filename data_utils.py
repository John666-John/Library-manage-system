# data_utils.py
import os
import json
import csv
import hashlib
import datetime
import shutil

# 数据存储路径
DATA_DIR = os.path.join(os.getcwd(), "data")
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BORROW_RECORDS_FILE = os.path.join(DATA_DIR, "borrow_records.csv")
BACKUP_DIR = os.path.join(os.getcwd(), "backup")

def init_data_dir():
    """初始化数据目录"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    # 初始化空文件（如果不存在）
    for file in [BOOKS_FILE, USERS_FILE]:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    if not os.path.exists(BORROW_RECORDS_FILE):
        with open(BORROW_RECORDS_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["borrower", "book_id", "book_title", "borrow_time", "due_time", "actual_return_time"])
            writer.writeheader()

def encrypt_password(password):
    """密码加密（MD5）"""
    return hashlib.md5(password.encode()).hexdigest()

def load_json(file_path):
    """加载JSON文件"""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_json(file_path, data):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_csv(file_path):
    """加载CSV文件"""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except:
        return []

def save_csv(file_path, data):
    """保存CSV文件"""
    if not data:
        return
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def backup_data():
    """备份数据"""
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(BACKUP_DIR, date_str)
    os.makedirs(backup_dir, exist_ok=True)
    for file in [BOOKS_FILE, USERS_FILE, BORROW_RECORDS_FILE]:
        if os.path.exists(file):
            shutil.copy(file, os.path.join(backup_dir, os.path.basename(file)))
    return backup_dir

def check_auto_backup():
    """每日首次启动自动备份"""
    today = datetime.date.today().strftime("%Y%m%d")
    backup_flag = os.path.join(DATA_DIR, f"backup_{today}.flag")
    if not os.path.exists(backup_flag):
        backup_data()
        with open(backup_flag, 'w') as f:
            f.write("")

def import_data(file_path):
    """导入已备份的数据记录，与当前数据记录合并去重"""
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.json':
        # 处理 JSON 文件（如 books.json, users.json）
        data = load_json(file_path)
        if 'id' in data[0]:  # 假设是图书数据
            current_books = load_json('data/books.json')
            current_book_ids = {book['id'] for book in current_books}
            new_books = [book for book in data if book['id'] not in current_book_ids]
            current_books.extend(new_books)
            save_json('data/books.json', current_books)
        elif 'username' in data[0]:  # 假设是用户数据
            current_users = load_json('data/users.json')
            current_usernames = {user['username'] for user in current_users}
            new_users = [user for user in data if user['username'] not in current_usernames]
            current_users.extend(new_users)
            save_json('data/users.json', current_users)
    elif file_ext == '.csv':
        # 处理 CSV 文件（如 borrow_records.csv）
        data = load_csv(file_path)
        current_records = load_csv('data/borrow_records.csv')
        current_record_keys = {(r['borrower'], r['book_id'], r['borrow_time']) for r in current_records}
        new_records = [r for r in data if (r['borrower'], r['book_id'], r['borrow_time']) not in current_record_keys]
        current_records.extend(new_records)
        save_csv('data/borrow_records.csv', current_records)