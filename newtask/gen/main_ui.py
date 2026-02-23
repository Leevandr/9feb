from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(900, 650)
        self.verticalLayout = QtWidgets.QVBoxLayout(MainForm)
        self.verticalLayout.setObjectName("verticalLayout")

        # --- Строка фильтров 1 ---
        self.filter_layout_1 = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit(MainForm)
        self.search_edit.setPlaceholderText("Поиск по названию или производителю")
        self.filter_layout_1.addWidget(self.search_edit)

        self.category_combo = QtWidgets.QComboBox(MainForm)
        self.category_combo.setMinimumWidth(130)
        self.filter_layout_1.addWidget(self.category_combo)

        self.material_combo = QtWidgets.QComboBox(MainForm)
        self.material_combo.setMinimumWidth(120)
        self.filter_layout_1.addWidget(self.material_combo)

        self.purpose_combo = QtWidgets.QComboBox(MainForm)
        self.purpose_combo.setMinimumWidth(160)
        self.filter_layout_1.addWidget(self.purpose_combo)

        self.verticalLayout.addLayout(self.filter_layout_1)

        # --- Строка фильтров 2 ---
        self.filter_layout_2 = QtWidgets.QHBoxLayout()

        self.price_min = QtWidgets.QSpinBox(MainForm)
        self.price_min.setMaximum(999999)
        self.price_min.setPrefix("от ")
        self.price_min.setSuffix(" руб")
        self.filter_layout_2.addWidget(self.price_min)

        self.price_max = QtWidgets.QSpinBox(MainForm)
        self.price_max.setMaximum(999999)
        self.price_max.setPrefix("до ")
        self.price_max.setSuffix(" руб")
        self.filter_layout_2.addWidget(self.price_max)

        self.search_btn = QtWidgets.QPushButton("Искать", MainForm)
        self.filter_layout_2.addWidget(self.search_btn)

        self.reset_btn = QtWidgets.QPushButton("Сброс", MainForm)
        self.filter_layout_2.addWidget(self.reset_btn)

        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.filter_layout_2.addItem(spacer)

        self.add_to_cart_btn = QtWidgets.QPushButton("В корзину", MainForm)
        self.filter_layout_2.addWidget(self.add_to_cart_btn)

        self.cart_btn = QtWidgets.QPushButton("Корзина (0)", MainForm)
        self.filter_layout_2.addWidget(self.cart_btn)

        self.auth_btn = QtWidgets.QPushButton("Авторизация", MainForm)
        self.filter_layout_2.addWidget(self.auth_btn)

        self.verticalLayout.addLayout(self.filter_layout_2)

        # --- Таблица товаров ---
        self.table = QtWidgets.QTableWidget(MainForm)
        self.verticalLayout.addWidget(self.table)

        # --- Счётчик ---
        self.count_label = QtWidgets.QLabel("Товаров: 0", MainForm)
        self.verticalLayout.addWidget(self.count_label)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Магазин канцелярии"))
