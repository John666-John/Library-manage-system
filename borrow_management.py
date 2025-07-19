import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                             QTextEdit, QMessageBox, QHeaderView, QApplication, QDialog)
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
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_available_books)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.refresh_btn)
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
        """归还图书（修复方法缺失问题，严格符合需求3.1.3）"""
        try:
            # 1. 加载当前用户未归还记录（需求3.1.3：仅处理未归还数据）
            records = load_csv(BORROW_RECORDS_FILE)
            user_unreturned = [
                r for r in records
                if r["borrower"] == self.user["username"]
                   and not r["actual_return_time"].strip()  # 未归还标识（需求3.1.3）
            ]

            if not user_unreturned:
                QMessageBox.information(self, "提示", "无未归还图书")
                return

            # 2. 弹出归还对话框（需正确实现get_selected_record方法）
            dialog = ReturnDialog(user_unreturned)
            if dialog.exec_() != QDialog.Accepted:
                return

            # 3. 获取选中记录（关键修复：确保方法存在）
            selected_record = dialog.get_selected_record()
            if not selected_record:
                QMessageBox.warning(self, "错误", "未选择图书")
                return

            # 4. 更新借阅记录（需求3.1.3：标记实际归还时间）
            return_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for r in records:
                # 匹配唯一标识：借阅人+图书编号+借阅时间（需求3.1.3字段）
                if (r["borrower"] == selected_record["borrower"]
                        and r["book_id"] == selected_record["book_id"]
                        and r["borrow_time"] == selected_record["borrow_time"]):
                    r["actual_return_time"] = return_time
                    break

            # 5. 保存更新（符合需求3.3数据存储约束）
            save_csv(BORROW_RECORDS_FILE, records)

            # 6. 刷新可借阅列表（需求3.1.3：归还后更新状态）
            self.load_available_books()
            QMessageBox.information(self, "成功", "图书归还成功")

        except Exception as e:
            QMessageBox.critical(self, "操作失败", f"归还过程出错：{str(e)}")

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


# 配套ReturnDialog类（完整实现get_selected_record方法）
class ReturnDialog(QDialog):
    def __init__(self, records):
        super().__init__()
        self.records = records  # 未归还记录列表（需求3.1.3）
        self.selected_row = -1  # 选中行索引
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("选择归还图书")
        self.setFixedSize(600, 300)

        # 表格初始化（仅展示必要字段：需求3.1.3核心信息）
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["图书编号", "书名", "借阅时间", "应还时间"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 填充数据（严格对应需求3.1.3字段）
        self.table.setRowCount(len(self.records))
        for row, r in enumerate(self.records):
            self.table.setItem(row, 0, QTableWidgetItem(r["book_id"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["book_title"]))
            self.table.setItem(row, 2, QTableWidgetItem(r["borrow_time"]))
            self.table.setItem(row, 3, QTableWidgetItem(r["due_time"]))

        # 信号绑定：选中行变化时记录索引
        self.table.itemSelectionChanged.connect(self.on_row_selected)

        # 按钮布局（需求3.1.3交互流程）
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确认")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def on_row_selected(self):
        """记录选中行（需求3.1.3：需选择1条记录）"""
        selected = self.table.selectedItems()
        if selected:
            self.selected_row = selected[0].row()  # 记录选中行索引

    def get_selected_record(self):
        """返回选中记录（需求3.1.3：严格校验选中状态）"""
        if self.selected_row == -1 or self.selected_row >= len(self.records):
            return None  # 未选中或索引越界
        return self.records[self.selected_row]  # 返回选中记录

class RenewDialog(ReturnDialog):
    def __init__(self, records):
        super().__init__(records)
        self.setWindowTitle("选择要续借的图书")