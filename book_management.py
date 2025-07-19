import sys
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFormLayout, QHeaderView, QDialog, QApplication)
from PyQt5.QtCore import Qt
from data_utils import load_json, save_json, BOOKS_FILE, load_csv, BORROW_RECORDS_FILE


class BookManagementTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.books = []
        self.book_ids = set()  # 新增：用于快速校验图书编号唯一性
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入书名、作者或ISBN搜索")
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search_books)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_books)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.refresh_btn)
        layout.addLayout(search_layout)

        # 管理员操作按钮
        if self.user["role"] == "admin":
            btn_layout = QHBoxLayout()
            self.add_btn = QPushButton("添加图书")
            self.edit_btn = QPushButton("修改图书")
            self.delete_btn = QPushButton("删除图书")

            self.add_btn.clicked.connect(self.add_book)
            self.edit_btn.clicked.connect(self.edit_book)
            self.delete_btn.clicked.connect(self.delete_book)

            btn_layout.addWidget(self.add_btn)
            btn_layout.addWidget(self.edit_btn)
            btn_layout.addWidget(self.delete_btn)
            layout.addLayout(btn_layout)

        # 图书表格
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(8)
        self.book_table.setHorizontalHeaderLabels(["图书编号", "书名", "作者", "ISBN",
                                                   "出版社", "出版日期", "馆藏位置", "状态"])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.book_table)

        self.setLayout(layout)

    def load_books(self):
        """加载图书数据（优化：同步更新图书编号集合）"""
        self.books = load_json(BOOKS_FILE)
        self.book_ids = {book["id"] for book in self.books}  # 用集合存储编号，优化查询速度
        self.update_book_table(self.books)

    def update_book_table(self, books):
        """更新图书表格"""
        self.book_table.setRowCount(len(books))
        borrow_records = load_csv(BORROW_RECORDS_FILE)
        borrowed_ids = [r["book_id"] for r in borrow_records if not r["actual_return_time"]]

        for row, book in enumerate(books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book.get("id", "")))
            self.book_table.setItem(row, 1, QTableWidgetItem(book.get("title", "")))
            self.book_table.setItem(row, 2, QTableWidgetItem(book.get("author", "")))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.get("isbn", "")))
            self.book_table.setItem(row, 4, QTableWidgetItem(book.get("publisher", "")))
            self.book_table.setItem(row, 5, QTableWidgetItem(book.get("publish_date", "")))
            self.book_table.setItem(row, 6, QTableWidgetItem(book.get("location", "")))

            # 状态判断（在库/已借出）
            status = "已借出" if book["id"] in borrowed_ids else "在库"
            self.book_table.setItem(row, 7, QTableWidgetItem(status))

    def search_books(self):
        """搜索图书"""
        keyword = self.search_edit.text().lower().strip()
        if not keyword:
            self.load_books()
            return

        filtered = [b for b in self.books if
                    keyword in b.get("title", "").lower() or
                    keyword in b.get("author", "").lower() or
                    keyword in b.get("isbn", "").lower()]
        self.update_book_table(filtered)

    def add_book(self):
        """添加图书（优化：高效校验+异常处理）"""
        dialog = BookDialog()  # 使用QDialog的正确实现
        if dialog.exec_():
            new_book = dialog.get_book_data()
            book_id = new_book["id"]

            # 优化：通过集合快速校验唯一性（O(1)复杂度，替代原遍历方式）
            if book_id in self.book_ids:
                QMessageBox.warning(self, "警告", "图书编号已存在")
                return

            try:
                # 优化：增量更新数据，减少文件IO操作
                self.books.append(new_book)
                self.book_ids.add(book_id)  # 同步更新集合
                save_json(BOOKS_FILE, self.books)  # 保持原存储格式，符合需求3.3数据存储约束

                self.load_books()  # 刷新表格
                QMessageBox.information(self, "成功", "图书添加成功")
            except Exception as e:
                # 新增：异常捕获，避免程序退出
                QMessageBox.critical(self, "错误", f"添加失败：{str(e)}")

    # 以下为其他方法（保持不变，但确保异常处理）
    def edit_book(self):
        try:
            selected_rows = set(item.row() for item in self.book_table.selectedItems())
            if len(selected_rows) != 1:
                QMessageBox.warning(self, "警告", "请选择一本图书进行修改")
                return

            row = list(selected_rows)[0]
            book_id = self.book_table.item(row, 0).text()
            book_to_edit = next((b for b in self.books if b["id"] == book_id), None)

            if not book_to_edit:
                return

            dialog = BookDialog(book_to_edit)
            if dialog.exec_():
                updated_book = dialog.get_book_data()
                for i, b in enumerate(self.books):
                    if b["id"] == book_id:
                        self.books[i] = updated_book
                        break

                save_json(BOOKS_FILE, self.books)
                self.load_books()
                QMessageBox.information(self, "成功", "图书修改成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改失败：{str(e)}")

    def delete_book(self):
        try:
            selected_rows = set(item.row() for item in self.book_table.selectedItems())
            if not selected_rows:
                QMessageBox.warning(self, "警告", "请选择要删除的图书")
                return

            if QMessageBox.question(self, "确认",
                                    "确定要删除选中的图书吗？\n删除后不可恢复，相关借阅记录不受影响",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return

            book_ids = [self.book_table.item(row, 0).text() for row in selected_rows]
            self.books = [b for b in self.books if b["id"] not in book_ids]
            self.book_ids = {book["id"] for book in self.books}  # 同步更新集合
            save_json(BOOKS_FILE, self.books)
            self.load_books()
            QMessageBox.information(self, "成功", "图书删除成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败：{str(e)}")


# 优化：使用QDialog实现对话框，解决事件循环导致的卡顿
class BookDialog(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        self.book_data = book_data or {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("编辑图书" if self.book_data else "添加图书")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.id_edit = QLineEdit(self.book_data.get("id", ""))
        self.title_edit = QLineEdit(self.book_data.get("title", ""))
        self.author_edit = QLineEdit(self.book_data.get("author", ""))
        self.isbn_edit = QLineEdit(self.book_data.get("isbn", ""))
        self.publisher_edit = QLineEdit(self.book_data.get("publisher", ""))
        self.publish_date_edit = QLineEdit(self.book_data.get("publish_date", ""))
        self.location_edit = QLineEdit(self.book_data.get("location", ""))
        self.category_edit = QLineEdit(self.book_data.get("category", ""))
        self.price_edit = QLineEdit(str(self.book_data.get("price", "")))
        self.quantity_edit = QLineEdit(str(self.book_data.get("quantity", "1")))

        form_layout.addRow("图书编号*:", self.id_edit)
        form_layout.addRow("书名*:", self.title_edit)
        form_layout.addRow("作者*:", self.author_edit)
        form_layout.addRow("ISBN:", self.isbn_edit)
        form_layout.addRow("出版社:", self.publisher_edit)
        form_layout.addRow("出版日期:", self.publish_date_edit)
        form_layout.addRow("馆藏位置:", self.location_edit)
        form_layout.addRow("分类:", self.category_edit)
        form_layout.addRow("单价:", self.price_edit)
        form_layout.addRow("数量:", self.quantity_edit)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_book_data(self):
        return {
            "id": self.id_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "isbn": self.isbn_edit.text().strip(),
            "publisher": self.publisher_edit.text().strip(),
            "publish_date": self.publish_date_edit.text().strip(),
            "location": self.location_edit.text().strip(),
            "category": self.category_edit.text().strip(),
            "price": self.price_edit.text().strip(),
            "quantity": self.quantity_edit.text().strip()
        }