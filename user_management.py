# user_management.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from data_utils import load_json, save_json, USERS_FILE


class UserManagementTab(QWidget):
    def __init__(self, on_current_user_deleted=None):
        super().__init__()
        self.users = []
        self.on_current_user_deleted = on_current_user_deleted
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

        # 检查是否包含当前用户
        current_user_deleted = False
        current_username = None
        if hasattr(self.parent(), 'user'):
            current_username = self.parent().user["username"]

        # 获取要删除的用户名
        usernames_to_delete = []
        for row in selected_rows:
            username = self.users[row]["username"]
            usernames_to_delete.append(username)
            if username == current_username:
                current_user_deleted = True

        # 确认删除
        if QMessageBox.question(self, "确认",
                                f"确定删除选中的 {len(selected_rows)} 个用户？\n删除后不可恢复",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        # 执行删除
        self.users = [u for u in self.users if u["username"] not in usernames_to_delete]
        save_json(USERS_FILE, self.users)
        self.load_users()

        # 如果删除了当前用户，触发回调
        if current_user_deleted and self.on_current_user_deleted:
            self.on_current_user_deleted()

        QMessageBox.information(self, "成功", "用户删除成功")