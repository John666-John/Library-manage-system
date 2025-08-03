from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QHBoxLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QGroupBox, QLabel, QInputDialog)
import datetime
from data_utils import load_json, load_csv, save_csv

BOOKS_FILE = 'data/books.json'
BORROW_RECORDS_FILE = 'data/borrow_records.csv'


class BorrowManagementTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.books = []
        self.available_books = []
        self.borrowed_books = []
        self.all_borrowed_records = []  # 用于存储所有已借出记录，支持搜索功能
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标签页
        self.tabs = QTabWidget()

        # 可借阅图书标签页
        borrow_tab = QWidget()
        borrow_layout = QVBoxLayout(borrow_tab)

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入书名、作者或ISBN搜索可借阅图书")
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_books)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_available_books)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.refresh_btn)
        borrow_layout.addLayout(search_layout)

        # 可借阅图书表格
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(6)
        self.book_table.setHorizontalHeaderLabels(["图书编号", "书名", "作者", "ISBN",
                                                   "出版社", "馆藏位置"])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        borrow_layout.addWidget(self.book_table)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.borrow_btn = QPushButton("借阅选中图书")
        self.borrow_btn.clicked.connect(self.borrow_book)
        btn_layout.addWidget(self.borrow_btn)
        borrow_layout.addLayout(btn_layout)

        # 添加标签页
        self.tabs.addTab(borrow_tab, "可借阅图书")

        layout.addWidget(self.tabs)

        # 操作按钮 (跨标签页)
        btn_layout = QHBoxLayout()
        self.return_btn = QPushButton("归还图书")
        self.renew_btn = QPushButton("续借图书")

        self.return_btn.clicked.connect(self.return_book)
        self.renew_btn.clicked.connect(self.renew_book)

        btn_layout.addWidget(self.return_btn)
        btn_layout.addWidget(self.renew_btn)
        layout.addLayout(btn_layout)

        # 已借出图书标签页
        self.borrowed_group = QGroupBox("已借出图书")
        borrowed_layout = QVBoxLayout()

        # 已借出图书搜索区域
        borrowed_search_layout = QHBoxLayout()
        self.borrowed_search_edit = QLineEdit()
        self.borrowed_search_edit.setPlaceholderText("输入书名或借阅人搜索")
        self.borrowed_search_btn = QPushButton("搜索")
        self.borrowed_refresh_btn = QPushButton("刷新")

        self.borrowed_search_btn.clicked.connect(self.search_borrowed_books)
        self.borrowed_refresh_btn.clicked.connect(self.load_borrowed_books)

        borrowed_search_layout.addWidget(self.borrowed_search_edit)
        borrowed_search_layout.addWidget(self.borrowed_search_btn)
        borrowed_search_layout.addWidget(self.borrowed_refresh_btn)
        borrowed_layout.addLayout(borrowed_search_layout)

        self.borrowed_table = QTableWidget()
        self.borrowed_table.setColumnCount(5)
        self.borrowed_table.setHorizontalHeaderLabels(
            ["图书编号", "书名", "借阅时间", "应还时间", "借阅人"]
        )
        self.borrowed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        borrowed_layout.addWidget(self.borrowed_table)
        self.borrowed_group.setLayout(borrowed_layout)
        layout.addWidget(self.borrowed_group)

        self.setLayout(layout)

    def load_available_books(self):
        """加载可借阅图书"""
        self.books = load_json(BOOKS_FILE)
        borrow_records = load_csv(BORROW_RECORDS_FILE)
        borrowed_ids = {r["book_id"] for r in borrow_records if not r["actual_return_time"]}

        self.available_books = [b for b in self.books if b["id"] not in borrowed_ids]
        self.borrowed_books = [b for b in self.books if b["id"] in borrowed_ids]
        self.update_book_table(self.available_books)
        self.load_borrowed_books()

    def update_book_table(self, books):
        """更新图书表格"""
        self.book_table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book["id"]))
            self.book_table.setItem(row, 1, QTableWidgetItem(book["title"]))
            self.book_table.setItem(row, 2, QTableWidgetItem(book["author"]))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.get("isbn", "")))
            self.book_table.setItem(row, 4, QTableWidgetItem(book.get("publisher", "")))
            self.book_table.setItem(row, 5, QTableWidgetItem(book.get("location", "")))

    def load_borrowed_books(self):
        """加载当前已借出的图书"""
        records = load_csv(BORROW_RECORDS_FILE)
        user_borrowed = [r for r in records if not r["actual_return_time"]]

        # 按借阅时间倒序排序
        user_borrowed.sort(key=lambda r: r["borrow_time"], reverse=True)

        # 保存原始数据用于搜索
        self.all_borrowed_records = user_borrowed

        self.update_borrowed_table(user_borrowed)

    def update_borrowed_table(self, records):
        """更新已借出图书表格"""
        self.borrowed_table.setRowCount(len(records))
        for row, r in enumerate(records):
            self.borrowed_table.setItem(row, 0, QTableWidgetItem(r["book_id"]))
            self.borrowed_table.setItem(row, 1, QTableWidgetItem(r["book_title"]))
            self.borrowed_table.setItem(row, 2, QTableWidgetItem(r["borrow_time"]))
            self.borrowed_table.setItem(row, 3, QTableWidgetItem(r["due_time"]))
            self.borrowed_table.setItem(row, 4, QTableWidgetItem(r["borrower"]))

    def search_books(self):
        """搜索可借阅图书"""
        keyword = self.search_edit.text().lower().strip()
        if not keyword:
            self.update_book_table(self.available_books)
            return

        filtered = [b for b in self.available_books if
                    keyword in b.get("title", "").lower() or
                    keyword in b.get("author", "").lower() or
                    keyword in b.get("isbn", "").lower()]
        self.update_book_table(filtered)

    def search_borrowed_books(self):
        """搜索已借出图书（支持书名和借阅人）"""
        keyword = self.borrowed_search_edit.text().lower().strip()
        if not keyword:
            self.update_borrowed_table(self.all_borrowed_records)
            return

        # 过滤包含关键词的记录（书名或借阅人）
        filtered = [r for r in self.all_borrowed_records if
                    keyword in r.get("book_title", "").lower() or
                    keyword in r.get("borrower", "").lower()]

        self.update_borrowed_table(filtered)

    def borrow_book(self):
        """借阅图书"""
        selected_rows = set(item.row() for item in self.book_table.selectedItems())
        if len(selected_rows) != 1:
            QMessageBox.warning(self, "警告", "请选择一本图书进行借阅")
            return

        row = list(selected_rows)[0]
        book_id = self.book_table.item(row, 0).text()
        book_title = self.book_table.item(row, 1).text()

        # 弹出对话框输入借阅人名称
        borrower, ok = QInputDialog.getText(self, "输入借阅人名称", "请输入借阅人名称:")
        if not ok or not borrower:
            QMessageBox.warning(self, "警告", "未输入有效的借阅人名称")
            return

        # 创建借阅记录
        borrow_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        due_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        new_record = {
            "borrower": borrower,
            "book_id": book_id,
            "book_title": book_title,
            "borrow_time": borrow_time,
            "due_time": due_time,
            "actual_return_time": ""
        }

        records = load_csv(BORROW_RECORDS_FILE)
        records.append(new_record)
        save_csv(BORROW_RECORDS_FILE, records)

        # 刷新界面
        self.load_available_books()
        QMessageBox.information(self, "成功",
                                f"借阅成功\n借阅人: {borrower}\n借阅日期: {borrow_time}\n应还日期: {due_time}")

    def return_book(self):
        """归还图书"""
        try:
            # 获取选中的记录
            selected_records = set(item.row() for item in self.borrowed_table.selectedItems())
            if len(selected_records) != 1:
                QMessageBox.warning(self, "警告", "请选择一本图书进行归还")
                return

            # 记录归还时间
            return_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = list(selected_records)[0]
            book_id = self.borrowed_table.item(row, 0).text()
            borrow_time = self.borrowed_table.item(row, 2).text()

            # 更新借阅记录
            records = load_csv(BORROW_RECORDS_FILE)
            for r in records:
                if r["book_id"] == book_id and r["borrow_time"] == borrow_time and not r["actual_return_time"]:
                    r["actual_return_time"] = return_time
                    break

            save_csv(BORROW_RECORDS_FILE, records)
            self.load_available_books()  # 刷新可借和已借列表
            QMessageBox.information(self, "成功", f"归还成功\n归还时间: {return_time}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"归还失败: {str(e)}")

    def renew_book(self):
        """续借图书（最多续借1次，延长15天）"""
        try:
            selected_records = set(item.row() for item in self.borrowed_table.selectedItems())
            if len(selected_records) != 1:
                QMessageBox.warning(self, "警告", "请选择一本图书进行续借")
                return

            row = list(selected_records)[0]
            book_id = self.borrowed_table.item(row, 0).text()
            borrow_time = self.borrowed_table.item(row, 2).text()
            current_due_time = self.borrowed_table.item(row, 3).text()

            # 解析日期
            due_time_obj = datetime.datetime.strptime(current_due_time, "%Y-%m-%d %H:%M:%S")
            today = datetime.datetime.now()

            # 检查是否已过期
            if due_time_obj < today:
                QMessageBox.warning(self, "警告", "图书已过期，无法续借")
                return

            # 检查是否已续借过（简单判断：原借阅周期30天，若已延长则不再续借）
            original_borrow_time = datetime.datetime.strptime(borrow_time, "%Y-%m-%d %H:%M:%S")
            if (due_time_obj - original_borrow_time).days > 30:
                QMessageBox.warning(self, "警告", "图书已续借过一次，无法再次续借")
                return

            # 延长15天
            new_due_time = (due_time_obj + datetime.timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")

            # 更新记录
            records = load_csv(BORROW_RECORDS_FILE)
            for r in records:
                if r["book_id"] == book_id and r["borrow_time"] == borrow_time and not r["actual_return_time"]:
                    r["due_time"] = new_due_time
                    break

            save_csv(BORROW_RECORDS_FILE, records)
            self.load_borrowed_books()  # 刷新已借列表
            QMessageBox.information(self, "成功", f"续借成功\n新应还日期: {new_due_time}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"续借失败: {str(e)}")


class BorrowerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("请输入借阅人名称:")
        self.borrower_edit = QLineEdit()

        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(label)
        layout.addWidget(self.borrower_edit)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_borrower_name(self):
        return self.borrower_edit.text().strip()


class ReturnDialog(QDialog):
    def __init__(self, records):
        super().__init__()
        self.records = records
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["借阅人", "图书编号", "书名", "借阅时间", "应还时间", "状态"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(self.records))
        for row, r in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(r["borrower"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["book_id"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["book_title"]))
            self.table.setItem(row, 3, QTableWidgetItem(r["borrow_time"]))
            self.table.setItem(row, 4, QTableWidgetItem(r["due_time"]))
            self.table.setItem(row, 5, QTableWidgetItem("未归还"))
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_selected_record(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if len(selected_rows) != 1:
            return None
        row = list(selected_rows)[0]
        return self.records[row]


class RenewDialog(QDialog):
    def __init__(self, records):
        super().__init__()
        self.records = records
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["借阅人", "图书编号", "书名", "借阅时间", "应还时间", "状态"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(self.records))
        for row, r in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(r["borrower"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["book_id"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["book_title"]))
            self.table.setItem(row, 3, QTableWidgetItem(r["borrow_time"]))
            self.table.setItem(row, 4, QTableWidgetItem(r["due_time"]))
            self.table.setItem(row, 5, QTableWidgetItem("未归还"))
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_selected_record(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if len(selected_rows) != 1:
            return None
        row = list(selected_rows)[0]
        return self.records[row]
