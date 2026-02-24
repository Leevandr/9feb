from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(1050, 720)
        self.verticalLayout = QtWidgets.QVBoxLayout(MainForm)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        # --- Верхняя панель с фильтрами ---
        self.top_panel = QtWidgets.QWidget(MainForm)
        self.top_panel.setObjectName("top_panel")
        self.top_layout = QtWidgets.QVBoxLayout(self.top_panel)
        self.top_layout.setContentsMargins(15, 12, 15, 12)
        self.top_layout.setSpacing(8)

        # Строка фильтров 1
        self.filter_layout_1 = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit(self.top_panel)
        self.search_edit.setPlaceholderText(
            "Поиск по названию или действующему веществу...")
        self.search_edit.setMinimumHeight(34)
        self.filter_layout_1.addWidget(self.search_edit)

        self.disease_combo = QtWidgets.QComboBox(self.top_panel)
        self.disease_combo.setMinimumWidth(170)
        self.disease_combo.setMinimumHeight(34)
        self.filter_layout_1.addWidget(self.disease_combo)

        self.form_combo = QtWidgets.QComboBox(self.top_panel)
        self.form_combo.setMinimumWidth(130)
        self.form_combo.setMinimumHeight(34)
        self.filter_layout_1.addWidget(self.form_combo)

        self.manufacturer_combo = QtWidgets.QComboBox(self.top_panel)
        self.manufacturer_combo.setMinimumWidth(160)
        self.manufacturer_combo.setMinimumHeight(34)
        self.filter_layout_1.addWidget(self.manufacturer_combo)

        self.prescription_combo = QtWidgets.QComboBox(self.top_panel)
        self.prescription_combo.setMinimumWidth(150)
        self.prescription_combo.setMinimumHeight(34)
        self.filter_layout_1.addWidget(self.prescription_combo)

        self.top_layout.addLayout(self.filter_layout_1)

        # Строка фильтров 2
        self.filter_layout_2 = QtWidgets.QHBoxLayout()

        self.price_min = QtWidgets.QSpinBox(self.top_panel)
        self.price_min.setMaximum(999999)
        self.price_min.setPrefix("от ")
        self.price_min.setSuffix(" руб")
        self.price_min.setMinimumHeight(34)
        self.filter_layout_2.addWidget(self.price_min)

        self.price_max = QtWidgets.QSpinBox(self.top_panel)
        self.price_max.setMaximum(999999)
        self.price_max.setPrefix("до ")
        self.price_max.setSuffix(" руб")
        self.price_max.setMinimumHeight(34)
        self.filter_layout_2.addWidget(self.price_max)

        self.search_btn = QtWidgets.QPushButton("Искать", self.top_panel)
        self.search_btn.setMinimumHeight(34)
        self.search_btn.setObjectName("search_btn")
        self.filter_layout_2.addWidget(self.search_btn)

        self.reset_btn = QtWidgets.QPushButton("Сброс", self.top_panel)
        self.reset_btn.setMinimumHeight(34)
        self.filter_layout_2.addWidget(self.reset_btn)

        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.filter_layout_2.addItem(spacer)

        self.cart_btn = QtWidgets.QPushButton("Корзина (0)", self.top_panel)
        self.cart_btn.setMinimumHeight(34)
        self.cart_btn.setObjectName("cart_btn")
        self.filter_layout_2.addWidget(self.cart_btn)

        self.auth_btn = QtWidgets.QPushButton(
            "Авторизация", self.top_panel)
        self.auth_btn.setMinimumHeight(34)
        self.auth_btn.setObjectName("auth_btn")
        self.filter_layout_2.addWidget(self.auth_btn)

        self.top_layout.addLayout(self.filter_layout_2)
        self.verticalLayout.addWidget(self.top_panel)

        # --- Область карточек ---
        self.scroll_area = QtWidgets.QScrollArea(MainForm)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(
            QtWidgets.QFrame.Shape.NoFrame)
        self.scroll_container = QtWidgets.QWidget()
        self.cards_grid = QtWidgets.QGridLayout(self.scroll_container)
        self.cards_grid.setSpacing(18)
        self.cards_grid.setContentsMargins(18, 18, 18, 18)
        self.scroll_area.setWidget(self.scroll_container)
        self.verticalLayout.addWidget(self.scroll_area)

        # --- Нижняя панель ---
        self.bottom_panel = QtWidgets.QWidget(MainForm)
        self.bottom_layout = QtWidgets.QHBoxLayout(self.bottom_panel)
        self.bottom_layout.setContentsMargins(15, 6, 15, 6)
        self.count_label = QtWidgets.QLabel(
            "Препаратов: 0", self.bottom_panel)
        self.bottom_layout.addWidget(self.count_label)
        self.verticalLayout.addWidget(self.bottom_panel)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(
            _translate("MainForm", "Аптека — Каталог препаратов"))
