import os

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QPixmap

from gen.login_ui import Ui_LoginForm
from models.db_manager import authenticate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.setWindowTitle('Авторизация — TechShop')
        self.main_window = None

        logo_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            self.ui.logo_label.setPixmap(pix)

        self.ui.login_btn.clicked.connect(self.do_login)
        self.ui.guest_btn.clicked.connect(self.do_guest)

    def do_login(self):
        login = self.ui.login_edit.text().strip()
        password = self.ui.password_edit.text().strip()

        if not login or not password:
            QMessageBox.warning(
                self, 'Ошибка',
                'Пожалуйста, введите логин и пароль.')
            return

        user = authenticate(login, password)
        if user is None:
            QMessageBox.warning(
                self, 'Ошибка авторизации',
                'Неверный логин или пароль.\n'
                'Проверьте правильность введённых данных.')
            return

        self._open_main(user['Role'], user['FIO'])

    def do_guest(self):
        self._open_main('guest', 'Гость')

    def _open_main(self, role, fio):
        from ui.main_window import MainWindow
        self.main_window = MainWindow(role, fio, self)
        self.main_window.show()
        self.hide()

    def on_logout(self):
        self.ui.login_edit.clear()
        self.ui.password_edit.clear()
        self.show()
