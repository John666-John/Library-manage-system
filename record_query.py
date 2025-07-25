# record_query.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFileDialog, QHeaderView)
from data_utils import load_csv, BORROW_RECORDS_FILE, save_csv


class RecordQueryTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.records = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入书名、借阅人或图书编号搜索")
        self.search_btn = QPushButton("搜索")
        self.reset_btn = QPushButton("重置")

        self.search_btn.clicked.connect(self.search_records)
        self.reset_btn.clicked.connect(self.load_records)

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)
        layout.addLayout(search_layout)

        # 记录表格
        self.record_table = QTableWidget()
        self.record_table.setColumnCount(6)
        self.record_table.setHorizontalHeaderLabels(
            ["借阅人", "图书编号", "书名", "借阅时间", "应还时间", "实际归还时间"])
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.record_table)

        # 管理员导出功能
        if self.user["role"] == "admin":
            btn_layout = QHBoxLayout()
            self.export_btn = QPushButton("导出记录为CSV")
            self.export_btn.clicked.connect(self.export_records)
            btn_layout.addWidget(self.export_btn)
            layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_records(self):
        """加载借阅记录"""
        self.records = load_csv(BORROW_RECORDS_FILE)

        # 权限过滤：普通用户只能看自己的记录
        if self.user["role"] != "admin":
            self.records = [r for r in self.records if r["borrower"] == self.user["username"]]

        self.update_table(self.records)

    def update_table(self, records):
        """更新表格显示"""
        self.record_table.setRowCount(len(records))
        for row, r in enumerate(records):
            self.record_table.setItem(row, 0, QTableWidgetItem(r.get("borrower", "")))
            self.record_table.setItem(row, 1, QTableWidgetItem(r.get("book_id", "")))
            self.record_table.setItem(row, 2, QTableWidgetItem(r.get("book_title", "")))
            self.record_table.setItem(row, 3, QTableWidgetItem(r.get("borrow_time", "")))
            self.record_table.setItem(row, 4, QTableWidgetItem(r.get("due_time", "")))
            self.record_table.setItem(row, 5, QTableWidgetItem(r.get("actual_return_time", "未归还")))

    def search_records(self):
        """搜索记录"""
        keyword = self.search_edit.text().lower().strip()
        if not keyword:
            self.load_records()
            return

        filtered = [r for r in self.records if
                    keyword in r.get("book_title", "").lower() or
                    keyword in r.get("borrower", "").lower() or
                    keyword in r.get("book_id", "").lower()]
        self.update_table(filtered)

    def export_records(self):
        """导出记录（管理员）"""
        if not self.records:
            QMessageBox.warning(self, "警告", "没有记录可导出")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "CSV文件 (*.csv)")
        if not file_path:
            return

        try:
            save_csv(file_path, self.records)
            QMessageBox.information(self, "成功", f"记录已导出至:\n{file_path}")
        except Exception as e:
            QMessageBox.error(self, "错误", f"导出失败:\n{str(e)}")