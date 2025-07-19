import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                             QTextEdit, QMessageBox, QHeaderView, QApplication)
from PyQt5.QtCore import Qt
from data_utils import load_json, load_csv, save_csv, BOOKS_FILE, BORROW_RECORDS_FILE


class BorrowManagementTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.books = []
        self.available_books = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入书名、作者或ISBN搜索可借阅图书")
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_books)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # 可借阅图书表格
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(7)
        self.book_table.setHorizontalHeaderLabels(["图书编号", "书名", "作者", "ISBN",
                                                   "出版社", "出版日期", "馆藏位置"])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.book_table)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.borrow_btn = QPushButton("借阅选中图书")
        self.return_btn = QPushButton("归还图书")
        self.renew_btn = QPushButton("续借图书")

        self.borrow_btn.clicked.connect(self.borrow_book)
        self.return_btn.clicked.connect(self.return_book)
        self.renew_btn.clicked.connect(self.renew_book)

        btn_layout.addWidget(self.borrow_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addWidget(self.renew_btn)
        layout.addLayout(btn_layout)

        # 逾期提醒
        self.overdue_group = QGroupBox("逾期提醒")
        overdue_layout = QVBoxLayout()
        self.overdue_text = QTextEdit()
        self.overdue_text.setReadOnly(True)
        overdue_layout.addWidget(self.overdue_text)
        self.overdue_group.setLayout(overdue_layout)
        layout.addWidget(self.overdue_group)

        self.setLayout(layout)

    def load_available_books(self):
        """加载可借阅图书"""
        self.books = load_json(BOOKS_FILE)
        borrow_records = load_csv(BORROW_RECORDS_FILE)
        borrowed_ids = {r["book_id"] for r in borrow_records if not r["actual_return_time"]}

        self.available_books = [b for b in self.books if b["id"] not in borrowed_ids]
        self.update_book_table(self.available_books)
        self.check_overdue()

    def update_book_table(self, books):
        """更新图书表格"""
        self.book_table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book["id"]))
            self.book_table.setItem(row, 1, QTableWidgetItem(book["title"]))
            self.book_table.setItem(row, 2, QTableWidgetItem(book["author"]))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.get("isbn", "")))
            self.book_table.setItem(row, 4, QTableWidgetItem(book.get("publisher", "")))
            self.book_table.setItem(row, 5, QTableWidgetItem(book.get("publish_date", "")))
            self.book_table.setItem(row, 6, QTableWidgetItem(book.get("location", "")))

    def search_books(self):
        """搜索可借阅图书"""
        keyword = self.search_edit.text().lower().strip()
        if not keyword:
            self.load_available_books()
            return

        filtered = [b for b in self.available_books if
                    keyword in b.get("title", "").lower() or
                    keyword in b.get("author", "").lower() or
                    keyword in b.get("isbn", "").lower()]
        self.update_book_table(filtered)

    def borrow_book(self):
        """借阅图书"""
        selected_rows = set(item.row() for item in self.book_table.selectedItems())
        if len(selected_rows) != 1:
            QMessageBox.warning(self, "警告", "请选择一本图书进行借阅")
            return

        row = list(selected_rows)[0]
        book_id = self.book_table.item(row, 0).text()
        book_title = self.book_table.item(row, 1).text()

        # 创建借阅记录
        borrow_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        due_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        new_record = {
            "borrower": self.user["username"],
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
        QMessageBox.information(self, "成功", f"借阅成功\n借阅日期: {borrow_time}\n应还日期: {due_time}")

    def return_book(self):
        """归还图书"""
        records = load_csv(BORROW_RECORDS_FILE)
        user_borrowed = [r for r in records if r["borrower"] == self.user["username"] and not r["actual_return_time"]]

        if not user_borrowed:
            QMessageBox.information(self, "提示", "您没有未归还的图书")
            return

        # 显示可归还图书列表
        dialog = ReturnDialog(user_borrowed)
        if dialog.exec_():
            selected_record = dialog.get_selected_record()
            if not selected_record:
                return

            # 更新归还时间
            return_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for r in records:
                if (r["borrower"] == selected_record["borrower"] and
                        r["book_id"] == selected_record["book_id"] and
                        r["borrow_time"] == selected_record["borrow_time"]):
                    r["actual_return_time"] = return_time
                    break

            save_csv(BORROW_RECORDS_FILE, records)

            # 检查逾期
            due_time = datetime.datetime.strptime(selected_record["due_time"], "%Y-%m-%d %H:%M:%S")
            actual_return = datetime.datetime.strptime(return_time, "%Y-%m-%d %H:%M:%S")
            if actual_return > due_time:
                days = (actual_return - due_time).days
                QMessageBox.information(self, "逾期提醒", f"已逾期 {days} 天，请按规定缴纳罚款")

            self.load_available_books()
            QMessageBox.information(self, "成功", "归还成功")

    def renew_book(self):
        """续借图书"""
        records = load_csv(BORROW_RECORDS_FILE)
        user_borrowed = [r for r in records if r["borrower"] == self.user["username"] and not r["actual_return_time"]]

        if not user_borrowed:
            QMessageBox.information(self, "提示", "您没有可续借的图书")
            return

        dialog = RenewDialog(user_borrowed)
        if dialog.exec_():
            selected_record = dialog.get_selected_record()
            if not selected_record:
                return

            # 检查是否逾期
            now = datetime.datetime.now()
            due_time = datetime.datetime.strptime(selected_record["due_time"], "%Y-%m-%d %H:%M:%S")
            if now > due_time:
                QMessageBox.warning(self, "警告", "图书已逾期，无法续借")
                return

            # 检查续借次数（默认最多1次）
            borrow_time = datetime.datetime.strptime(selected_record["borrow_time"], "%Y-%m-%d %H:%M:%S")
            if (due_time - borrow_time) > datetime.timedelta(days=31):  # 超过31天视为已续借
                QMessageBox.warning(self, "警告", "最多续借1次")
                return

            # 续借15天
            new_due = (due_time + datetime.timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")
            for r in records:
                if (r["borrower"] == selected_record["borrower"] and
                        r["book_id"] == selected_record["book_id"] and
                        r["borrow_time"] == selected_record["borrow_time"]):
                    r["due_time"] = new_due
                    break

            save_csv(BORROW_RECORDS_FILE, records)
            QMessageBox.information(self, "成功", f"续借成功，新应还日期: {new_due}")

    def check_overdue(self):
        """检查逾期图书"""
        records = load_csv(BORROW_RECORDS_FILE)
        now = datetime.datetime.now()
        overdue = []

        for r in records:
            if r["borrower"] == self.user["username"] and not r["actual_return_time"]:
                due = datetime.datetime.strptime(r["due_time"], "%Y-%m-%d %H:%M:%S")
                if now > due:
                    days = (now - due).days
                    overdue.append(f"• 《{r['book_title']}》(编号: {r['book_id']}) 逾期 {days} 天")

        if overdue:
            self.overdue_text.setText("\n".join(overdue))
            self.overdue_group.setTitle(f"逾期提醒 ({len(overdue)})")
        else:
            self.overdue_text.setText("无逾期图书")


class ReturnDialog(QWidget):
    def __init__(self, records):
        super().__init__()
        self.records = records
        self.selected_record = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("选择要归还的图书")
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["图书编号", "书名", "借阅日期", "应还日期", "借阅人"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 填充数据
        self.table.setRowCount(len(self.records))
        for row, r in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(r["book_id"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["book_title"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["borrow_time"]))
            self.table.setItem(row, 3, QTableWidgetItem(r["due_time"]))
            self.table.setItem(row, 4, QTableWidgetItem(r["borrower"]))

        layout.addWidget(self.table)

        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定归还")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setModal(True)

    def get_selected_record(self):
        return self.selected_record

    def accept(self):
        rows = set(item.row() for item in self.table.selectedItems())
        if len(rows) != 1:
            QMessageBox.warning(self, "警告", "请选择一本图书")
            return
        self.selected_record = self.records[list(rows)[0]]
        self.close()

    def reject(self):
        self.selected_record = None
        self.close()

    def exec_(self):
        self.show()
        self.exec_loop = True
        while self.exec_loop:
            QApplication.processEvents()
        return self.selected_record is not None


class RenewDialog(ReturnDialog):
    def __init__(self, records):
        super().__init__(records)
        self.setWindowTitle("选择要续借的图书")