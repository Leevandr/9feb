"""Окно авторизации."""
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from models.db_manager import authenticate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация — TechShop')
        self.setFixedSize(400, 350)
        self.main_window = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        # Логотип
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            logo_label.setPixmap(pix)
        layout.addWidget(logo_label)

        layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Fixed))

        title = QLabel('Вход в систему')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText('Логин')
        layout.addWidget(self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Пароль')
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)

        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton('Войти')
        self.login_btn.setObjectName('login_btn')
        self.login_btn.clicked.connect(self.do_login)
        btn_layout.addWidget(self.login_btn)

        self.guest_btn = QPushButton('Войти как гость')
        self.guest_btn.setObjectName('guest_btn')
        self.guest_btn.clicked.connect(self.do_guest)
        btn_layout.addWidget(self.guest_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def do_login(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()

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
        """Вызывается при выходе из учётной записи."""
        self.login_edit.clear()
        self.password_edit.clear()
        self.show()
