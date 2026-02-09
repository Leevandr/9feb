from PyQt6 import QtWidgets


class Ui_AuthForm(object):
    def setupUi(self, Form):
        Form.setObjectName("AuthForm")
        Form.resize(300, 200)
        Form.setWindowTitle("Авторизация")

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)

        self.login_edit = QtWidgets.QLineEdit(Form)
        self.login_edit.setPlaceholderText("Логин")
        self.verticalLayout.addWidget(self.login_edit)

        self.password_edit = QtWidgets.QLineEdit(Form)
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.verticalLayout.addWidget(self.password_edit)

        self.login_btn = QtWidgets.QPushButton("Войти", Form)
        self.verticalLayout.addWidget(self.login_btn)
