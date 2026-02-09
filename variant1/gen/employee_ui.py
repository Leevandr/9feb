from PyQt6 import QtWidgets


class Ui_EmployeeForm(object):
    def setupUi(self, Form):
        Form.setObjectName("EmployeeForm")
        Form.resize(900, 600)
        Form.setWindowTitle("Окно сотрудника")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)

        # --- Таблица книг ---
        self.table = QtWidgets.QTableWidget(Form)
        self.mainLayout.addWidget(self.table)

        # --- Форма ввода ---
        self.formLayout = QtWidgets.QHBoxLayout()

        self.title_edit = QtWidgets.QLineEdit(Form)
        self.title_edit.setPlaceholderText("Название")
        self.formLayout.addWidget(self.title_edit)

        self.author_edit = QtWidgets.QLineEdit(Form)
        self.author_edit.setPlaceholderText("Автор")
        self.formLayout.addWidget(self.author_edit)

        self.genre_edit = QtWidgets.QLineEdit(Form)
        self.genre_edit.setPlaceholderText("Жанр")
        self.formLayout.addWidget(self.genre_edit)

        self.photo_edit = QtWidgets.QLineEdit(Form)
        self.photo_edit.setPlaceholderText("Путь к фото")
        self.formLayout.addWidget(self.photo_edit)

        self.photo_browse_btn = QtWidgets.QPushButton("Обзор...", Form)
        self.formLayout.addWidget(self.photo_browse_btn)

        self.mainLayout.addLayout(self.formLayout)

        # --- Кнопки CRUD ---
        self.btnLayout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Добавить", Form)
        self.btnLayout.addWidget(self.add_btn)
        self.edit_btn = QtWidgets.QPushButton("Сохранить изменения", Form)
        self.btnLayout.addWidget(self.edit_btn)
        self.delete_btn = QtWidgets.QPushButton("Удалить", Form)
        self.btnLayout.addWidget(self.delete_btn)
        self.mainLayout.addLayout(self.btnLayout)
