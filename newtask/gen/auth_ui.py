from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AuthForm(object):
    def setupUi(self, AuthForm):
        AuthForm.setObjectName("AuthForm")
        AuthForm.resize(400, 350)
        self.verticalLayout = QtWidgets.QVBoxLayout(AuthForm)

        self.tabs = QtWidgets.QTabWidget(AuthForm)

        # ===== Вкладка «Вход» =====
        self.login_tab = QtWidgets.QWidget()
        self.login_layout = QtWidgets.QVBoxLayout(self.login_tab)

        self.login_header = QtWidgets.QLabel("Войти в систему", self.login_tab)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.login_header.setFont(font)
        self.login_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.login_layout.addWidget(self.login_header)

        self.login_email_edit = QtWidgets.QLineEdit(self.login_tab)
        self.login_email_edit.setPlaceholderText("E-mail")
        self.login_layout.addWidget(self.login_email_edit)

        self.login_password_edit = QtWidgets.QLineEdit(self.login_tab)
        self.login_password_edit.setPlaceholderText("Пароль")
        self.login_password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.login_layout.addWidget(self.login_password_edit)

        self.login_btn = QtWidgets.QPushButton("Войти", self.login_tab)
        self.login_layout.addWidget(self.login_btn)

        self.login_layout.addStretch()

        self.tabs.addTab(self.login_tab, "Вход")

        # ===== Вкладка «Регистрация» =====
        self.register_tab = QtWidgets.QWidget()
        self.register_layout = QtWidgets.QVBoxLayout(self.register_tab)

        self.register_header = QtWidgets.QLabel("Создать аккаунт", self.register_tab)
        font2 = QtGui.QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        self.register_header.setFont(font2)
        self.register_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.register_layout.addWidget(self.register_header)

        self.reg_fio_edit = QtWidgets.QLineEdit(self.register_tab)
        self.reg_fio_edit.setPlaceholderText("ФИО")
        self.register_layout.addWidget(self.reg_fio_edit)

        self.reg_email_edit = QtWidgets.QLineEdit(self.register_tab)
        self.reg_email_edit.setPlaceholderText("E-mail")
        self.register_layout.addWidget(self.reg_email_edit)

        self.reg_phone_edit = QtWidgets.QLineEdit(self.register_tab)
        self.reg_phone_edit.setPlaceholderText("Телефон")
        self.register_layout.addWidget(self.reg_phone_edit)

        self.reg_password_edit = QtWidgets.QLineEdit(self.register_tab)
        self.reg_password_edit.setPlaceholderText("Пароль")
        self.reg_password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.register_layout.addWidget(self.reg_password_edit)

        self.reg_password2_edit = QtWidgets.QLineEdit(self.register_tab)
        self.reg_password2_edit.setPlaceholderText("Повторите пароль")
        self.reg_password2_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.register_layout.addWidget(self.reg_password2_edit)

        self.register_btn = QtWidgets.QPushButton("Зарегистрироваться", self.register_tab)
        self.register_layout.addWidget(self.register_btn)

        self.register_layout.addStretch()

        self.tabs.addTab(self.register_tab, "Регистрация")

        self.verticalLayout.addWidget(self.tabs)

        self.retranslateUi(AuthForm)
        QtCore.QMetaObject.connectSlotsByName(AuthForm)

    def retranslateUi(self, AuthForm):
        _translate = QtCore.QCoreApplication.translate
        AuthForm.setWindowTitle(_translate("AuthForm", "Авторизация / Регистрация"))
