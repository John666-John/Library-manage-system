from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton,
                             QMessageBox)
from data_utils import load_json, save_json

USERS_FILE = 'data/users.json'

class UserManagementTab(QWidget):
    def __init__(self, handle_current_user_deleted, current_suer):
        super().__init__()
        self.handle_current_user_deleted = handle_current_user_deleted
        self.users = []
        self.init_ui()
        self.current_user = current_suer

    def init_ui(self):
        layout = QVBoxLayout()

        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["用户名", "角色"])
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
        self.update_user_table(self.users)

    def update_user_table(self, users):
        """更新用户表格"""
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(user["username"]))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["role"]))

    def delete_user(self):
        """删除选中用户"""
        selected_rows = set(item.row() for item in self.user_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请选择要删除的用户")
            return

        if QMessageBox.question(self, "确认",
                                "确定要删除选中的用户吗？",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return

        # 执行删除
        usernames = [self.users[row]["username"] for row in selected_rows]
        if self.current_user["username"] in usernames:
            if QMessageBox.question(self, "确认删除自身",
                                    "确定要删除当前登录的用户吗？删除后将自动退出登录",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return
        self.users = [u for u in self.users if u["username"] not in usernames]
        save_json(USERS_FILE, self.users)
        self.load_users()
        QMessageBox.information(self, "成功", "用户删除成功")
        if self.current_user["username"] in usernames:
            self.handle_current_user_deleted()
        #
        # for row in selected_rows:
        #     username = self.user_table.item(row, 0).text()
        #     if self.app.current_user["username"] == username:
        #         if QMessageBox.question(self, "确认删除自身",
        #                                 "确定要删除当前登录的用户吗？删除后将自动退出登录",
        #                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
        #             self.users = [user for user in self.users if user["username"] != username]
        #             save_json(USERS_FILE, self.users)
        #             self.handle_current_user_deleted()
        #         return
        #
        #     self.users = [user for user in self.users if user["username"] != username]
        #
        # save_json(USERS_FILE, self.users)
        # self.load_users()
        # QMessageBox.information(self, "成功", "用户删除成功")