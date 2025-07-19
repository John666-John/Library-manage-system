import sys
import os
from PyQt5.QtWidgets import QApplication
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

    def check_backup(self):
        """检查每日自动备份"""
        check_auto_backup()

    def show_main_window(self, user):
        """切换到主窗口"""
        self.current_user = user
        self.main_window = MainWindow(self, user)
        self.main_window.show()
        self.login_window.close()


if __name__ == "__main__":
    app = LibrarySystem(sys.argv)
    sys.exit(app.exec_())