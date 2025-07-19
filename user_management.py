from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from data_utils import load_json, save_json, USERS_FILE


class UserManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.users = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["用户名", "联系方式", "身份证号", "用户类型"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("删除选中用户")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_users(self):
        """加载用户数据"""
        self.users = load_json(USERS_FILE)
        self.update_user_table()

    def update_user_table(self):
        """更新用户表格"""
        self.user_table.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            self.user_table.setItem(row, 0, QTableWidgetItem(user["username"]))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["contact"]))
            self.user_table.setItem(row, 2, QTableWidgetItem(user["id_card"]))  # 实际应用中需脱敏
            self.user_table.setItem(row, 3, QTableWidgetItem("管理员" if user["role"] == "admin" else "普通用户"))

    def delete_user(self):
        """删除用户（管理员）"""
        selected_rows = set(item.row() for item in self.user_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请选择要删除的用户")
            return

        if QMessageBox.question(self, "确认", f"确定删除选中的 {len(selected_rows)} 个用户？",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        # 执行删除
        usernames = [self.users[row]["username"] for row in selected_rows]
        self.users = [u for u in self.users if u["username"] not in usernames]
        save_json(USERS_FILE, self.users)
        self.load_users()
        QMessageBox.information(self, "成功", "用户删除成功")