from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt


class Ui_LoginForm:
    def setupUi(self, widget):
        widget.setFixedSize(400, 350)

        self.main_layout = QVBoxLayout(widget)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(12)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.logo_label)

        self.main_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Fixed))

        self.title_label = QLabel('Вход в систему')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            'font-size: 18px; font-weight: bold;')
        self.main_layout.addWidget(self.title_label)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText('Логин')
        self.main_layout.addWidget(self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Пароль')
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.main_layout.addWidget(self.password_edit)

        self.btn_layout = QHBoxLayout()

        self.login_btn = QPushButton('Войти')
        self.login_btn.setObjectName('login_btn')
        self.btn_layout.addWidget(self.login_btn)

        self.guest_btn = QPushButton('Войти как гость')
        self.guest_btn.setObjectName('guest_btn')
        self.btn_layout.addWidget(self.guest_btn)

        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addStretch()
