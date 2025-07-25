# main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QMenuBar, QMenu, QAction, QMessageBox)
from PyQt5.QtGui import QIcon
from book_management import BookManagementTab
from borrow_management import BorrowManagementTab
from record_query import RecordQueryTab
from user_management import UserManagementTab
from data_utils import backup_data


class MainWindow(QMainWindow):
    def __init__(self, app, user):
        super().__init__()
        self.app = app
        self.user = user
        self.init_ui()

    def handle_current_user_deleted(self):
        """处理当前用户被删除的情况"""
        self.app.logout()

    def init_ui(self):
        self.setWindowTitle(
            f"图书管理系统 - {self.user['username']} ({'管理员' if self.user['role'] == 'admin' else '用户'})")
        self.setGeometry(100, 100, 1000, 600)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 标签页
        self.tabs = QTabWidget()
        self.book_tab = BookManagementTab(self.user)
        self.borrow_tab = BorrowManagementTab(self.user)
        self.record_tab = RecordQueryTab(self.user)

        self.tabs.addTab(self.book_tab, "图书管理")
        self.tabs.addTab(self.borrow_tab, "借阅管理")
        self.tabs.addTab(self.record_tab, "记录查询")

        # 管理员专属标签
        if self.user["role"] == "admin":
            self.user_tab = UserManagementTab(self.handle_current_user_deleted)
            self.tabs.addTab(self.user_tab, "用户管理")

        main_layout.addWidget(self.tabs)

        # 菜单栏
        self.create_menu_bar()

        # 加载数据
        self.book_tab.load_books()
        self.borrow_tab.load_available_books()
        self.record_tab.load_records()
        if self.user["role"] == "admin":
            self.user_tab.load_users()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 系统菜单
        sys_menu = menubar.addMenu("系统")

        # 备份
        backup_action = QAction("备份数据", self)
        backup_action.triggered.connect(self.backup_data)
        sys_menu.addAction(backup_action)

        # 退出登录
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        sys_menu.addAction(logout_action)

        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        sys_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def logout(self):
        """退出登录"""
        if QMessageBox.question(
                self, "确认退出",
                "确定要退出当前账号吗？",
                QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.app.logout()

    def backup_data(self):
        """手动备份数据"""
        try:
            backup_dir = backup_data()
            QMessageBox.information(self, "成功", f"数据已备份至:\n{backup_dir}")
        except Exception as e:
            QMessageBox.error(self, "错误", f"备份失败:\n{str(e)}")

    def show_about(self):
        QMessageBox.about(self, "关于", "图书管理系统 v1.0\n基于PyQt5开发")