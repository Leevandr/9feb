from PyQt6 import QtWidgets


class Ui_MainForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 600)
        Form.setWindowTitle("Библиотека")

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)

        # --- верхняя панель фильтров ---
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.author_edit = QtWidgets.QLineEdit(Form)
        self.author_edit.setPlaceholderText("Автор")
        self.horizontalLayout.addWidget(self.author_edit)

        self.genre_combo = QtWidgets.QComboBox(Form)
        self.horizontalLayout.addWidget(self.genre_combo)

        self.search_btn = QtWidgets.QPushButton("Искать", Form)
        self.horizontalLayout.addWidget(self.search_btn)

        self.reset_btn = QtWidgets.QPushButton("Сброс", Form)
        self.horizontalLayout.addWidget(self.reset_btn)

        self.auth_btn = QtWidgets.QPushButton("Авторизация", Form)
        self.horizontalLayout.addWidget(self.auth_btn)

        self.verticalLayout.addLayout(self.horizontalLayout)

        # --- таблица ---
        self.table = QtWidgets.QTableWidget(Form)
        self.verticalLayout.addWidget(self.table)
