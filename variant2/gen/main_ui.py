from PyQt6 import QtWidgets


class Ui_MainForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 600)
        Form.setWindowTitle("Магазин электроники")

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)

        # --- верхняя панель фильтров ---
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.search_edit = QtWidgets.QLineEdit(Form)
        self.search_edit.setPlaceholderText("Артикул или название")
        self.horizontalLayout.addWidget(self.search_edit)

        self.category_combo = QtWidgets.QComboBox(Form)
        self.horizontalLayout.addWidget(self.category_combo)

        self.price_min = QtWidgets.QSpinBox(Form)
        self.price_min.setMaximum(999999)
        self.price_min.setPrefix("от ")
        self.horizontalLayout.addWidget(self.price_min)

        self.price_max = QtWidgets.QSpinBox(Form)
        self.price_max.setMaximum(999999)
        self.price_max.setPrefix("до ")
        self.horizontalLayout.addWidget(self.price_max)

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
