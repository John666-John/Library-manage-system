# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from main_window import MainWindow
from login_window import LoginWindow
from data_utils import init_data_dir, check_auto_backup

# 初始化数据目录
init_data_dir()


class LibrarySystem(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.current_user = None
        self.check_backup()  # 检查自动备份
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def handle_current_user_deleted(self):
        """处理当前用户被删除的情况"""
        QMessageBox.information(
            self.login_window,
            "用户已删除",
            "您的账号已被删除，系统将退出"
        )
        self.quit()

    def check_backup(self):
        """检查每日自动备份"""
        check_auto_backup()

    def show_main_window(self, user):
        """切换到主窗口"""
        self.current_user = user
        self.main_window = MainWindow(self, user)
        self.main_window.show()
        self.login_window.close()

    def logout(self):
        """退出到登录界面"""
        self.current_user = None
        self.login_window = LoginWindow(self)
        self.login_window.show()
        if hasattr(self, 'main_window'):
            self.main_window.close()


if __name__ == "__main__":
    app = LibrarySystem(sys.argv)
    sys.exit(app.exec_())