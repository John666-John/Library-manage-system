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