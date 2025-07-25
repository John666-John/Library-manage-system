# login_window.py
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFormLayout, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from data_utils import load_json, save_json, USERS_FILE, encrypt_password


class LoginWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("图书管理系统 - 登录")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("图书管理系统")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 登录表单
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        form_layout.addRow("用户名:", self.username_edit)
        form_layout.addRow("密码:", self.password_edit)
        layout.addLayout(form_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("登录")
        self.register_btn = QPushButton("注册")

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.show_register)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def login(self):
        """处理登录逻辑"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空")
            return

        users = load_json(USERS_FILE)
        encrypted_pwd = encrypt_password(password)

        for user in users:
            if user["username"] == username and user["password"] == encrypted_pwd:
                QMessageBox.information(self, "成功", f"欢迎回来，{username}！")
                self.app.show_main_window(user)
                return

        QMessageBox.error(self, "错误", "用户名或密码错误")

    def show_register(self):
        """显示注册窗口"""
        self.register_window = RegisterWindow()
        self.register_window.show()


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("用户注册")
        self.setGeometry(150, 150, 400, 400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.contact_edit = QLineEdit()
        self.id_edit = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["普通用户", "管理员"])

        form_layout.addRow("用户名:", self.username_edit)
        form_layout.addRow("密码:", self.password_edit)
        form_layout.addRow("确认密码:", self.confirm_edit)
        form_layout.addRow("联系方式:", self.contact_edit)
        form_layout.addRow("身份证号:", self.id_edit)
        form_layout.addRow("用户类型:", self.role_combo)

        layout.addLayout(form_layout)

        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def register(self):
        """处理注册逻辑"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm = self.confirm_edit.text().strip()
        contact = self.contact_edit.text().strip()
        id_card = self.id_edit.text().strip()
        role = "admin" if self.role_combo.currentText() == "管理员" else "user"

        if not all([username, password, confirm, contact, id_card]):
            QMessageBox.warning(self, "警告", "所有字段不能为空")
            return

        if password != confirm:
            QMessageBox.warning(self, "警告", "两次密码不一致")
            return

        users = load_json(USERS_FILE)
        for user in users:
            if user["username"] == username:
                QMessageBox.warning(self, "警告", "用户名已存在")
                return

        new_user = {
            "username": username,
            "password": encrypt_password(password),
            "contact": contact,
            "id_card": id_card,
            "role": role
        }

        users.append(new_user)
        save_json(USERS_FILE, users)
        QMessageBox.information(self, "成功", "注册成功，请登录")
        self.close()