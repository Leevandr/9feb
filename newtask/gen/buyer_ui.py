from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_BuyerForm(object):
    def setupUi(self, BuyerForm):
        BuyerForm.setObjectName("BuyerForm")
        BuyerForm.resize(1050, 720)
        self.mainLayout = QtWidgets.QVBoxLayout(BuyerForm)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QtWidgets.QTabWidget(BuyerForm)

        # ===== Вкладка «Каталог» =====
        self.catalog_tab = QtWidgets.QWidget()
        self.catalog_layout = QtWidgets.QVBoxLayout(self.catalog_tab)
        self.catalog_layout.setContentsMargins(0, 0, 0, 0)
        self.catalog_layout.setSpacing(0)

        # Панель фильтров
        self.filter_panel = QtWidgets.QWidget(self.catalog_tab)
        self.filter_panel_layout = QtWidgets.QVBoxLayout(self.filter_panel)
        self.filter_panel_layout.setContentsMargins(15, 10, 15, 10)
        self.filter_panel_layout.setSpacing(8)

        self.cat_filter_1 = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit(self.filter_panel)
        self.search_edit.setPlaceholderText(
            "Поиск по названию или действующему веществу...")
        self.search_edit.setMinimumHeight(34)
        self.cat_filter_1.addWidget(self.search_edit)

        self.disease_combo = QtWidgets.QComboBox(self.filter_panel)
        self.disease_combo.setMinimumWidth(170)
        self.disease_combo.setMinimumHeight(34)
        self.cat_filter_1.addWidget(self.disease_combo)

        self.form_combo = QtWidgets.QComboBox(self.filter_panel)
        self.form_combo.setMinimumWidth(130)
        self.form_combo.setMinimumHeight(34)
        self.cat_filter_1.addWidget(self.form_combo)

        self.manufacturer_combo = QtWidgets.QComboBox(self.filter_panel)
        self.manufacturer_combo.setMinimumWidth(160)
        self.manufacturer_combo.setMinimumHeight(34)
        self.cat_filter_1.addWidget(self.manufacturer_combo)

        self.prescription_combo = QtWidgets.QComboBox(self.filter_panel)
        self.prescription_combo.setMinimumWidth(150)
        self.prescription_combo.setMinimumHeight(34)
        self.cat_filter_1.addWidget(self.prescription_combo)

        self.filter_panel_layout.addLayout(self.cat_filter_1)

        self.cat_filter_2 = QtWidgets.QHBoxLayout()

        self.price_min = QtWidgets.QSpinBox(self.filter_panel)
        self.price_min.setMaximum(999999)
        self.price_min.setPrefix("от ")
        self.price_min.setSuffix(" руб")
        self.price_min.setMinimumHeight(34)
        self.cat_filter_2.addWidget(self.price_min)

        self.price_max = QtWidgets.QSpinBox(self.filter_panel)
        self.price_max.setMaximum(999999)
        self.price_max.setPrefix("до ")
        self.price_max.setSuffix(" руб")
        self.price_max.setMinimumHeight(34)
        self.cat_filter_2.addWidget(self.price_max)

        self.search_btn = QtWidgets.QPushButton(
            "Искать", self.filter_panel)
        self.search_btn.setMinimumHeight(34)
        self.search_btn.setObjectName("search_btn")
        self.cat_filter_2.addWidget(self.search_btn)

        self.reset_btn = QtWidgets.QPushButton(
            "Сброс", self.filter_panel)
        self.reset_btn.setMinimumHeight(34)
        self.cat_filter_2.addWidget(self.reset_btn)

        self.filter_panel_layout.addLayout(self.cat_filter_2)
        self.catalog_layout.addWidget(self.filter_panel)

        # Область карточек
        self.scroll_area = QtWidgets.QScrollArea(self.catalog_tab)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(
            QtWidgets.QFrame.Shape.NoFrame)
        self.scroll_container = QtWidgets.QWidget()
        self.cards_grid = QtWidgets.QGridLayout(self.scroll_container)
        self.cards_grid.setSpacing(18)
        self.cards_grid.setContentsMargins(18, 18, 18, 18)
        self.scroll_area.setWidget(self.scroll_container)
        self.catalog_layout.addWidget(self.scroll_area)

        self.tabs.addTab(self.catalog_tab, "Каталог")

        # ===== Вкладка «Корзина» =====
        self.cart_tab = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout(self.cart_tab)
        self.cart_layout.setContentsMargins(15, 15, 15, 15)

        self.cart_table = QtWidgets.QTableWidget(self.cart_tab)
        self.cart_layout.addWidget(self.cart_table)

        self.cart_btn_layout = QtWidgets.QHBoxLayout()

        self.plus_btn = QtWidgets.QPushButton("+1", self.cart_tab)
        self.plus_btn.setMinimumHeight(34)
        self.cart_btn_layout.addWidget(self.plus_btn)

        self.minus_btn = QtWidgets.QPushButton("-1", self.cart_tab)
        self.minus_btn.setMinimumHeight(34)
        self.cart_btn_layout.addWidget(self.minus_btn)

        self.remove_btn = QtWidgets.QPushButton("Удалить", self.cart_tab)
        self.remove_btn.setMinimumHeight(34)
        self.cart_btn_layout.addWidget(self.remove_btn)

        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.cart_btn_layout.addItem(spacer)

        self.cart_total_label = QtWidgets.QLabel(
            "Итого: 0 руб", self.cart_tab)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.cart_total_label.setFont(font)
        self.cart_btn_layout.addWidget(self.cart_total_label)

        self.cart_layout.addLayout(self.cart_btn_layout)

        self.checkout_btn = QtWidgets.QPushButton(
            "Оформить заказ", self.cart_tab)
        self.checkout_btn.setMinimumHeight(40)
        self.checkout_btn.setObjectName("checkout_btn")
        self.cart_layout.addWidget(self.checkout_btn)

        self.tabs.addTab(self.cart_tab, "Корзина")

        # ===== Вкладка «Мои заказы» =====
        self.orders_tab = QtWidgets.QWidget()
        self.orders_layout = QtWidgets.QVBoxLayout(self.orders_tab)
        self.orders_layout.setContentsMargins(15, 15, 15, 15)

        self.orders_table = QtWidgets.QTableWidget(self.orders_tab)
        self.orders_layout.addWidget(self.orders_table)

        self.tabs.addTab(self.orders_tab, "Мои заказы")

        # ===== Вкладка «Профиль» =====
        self.profile_tab = QtWidgets.QWidget()
        self.profile_layout = QtWidgets.QVBoxLayout(self.profile_tab)
        self.profile_layout.setContentsMargins(20, 20, 20, 20)

        self.profile_fio = QtWidgets.QLabel("ФИО: ", self.profile_tab)
        font2 = QtGui.QFont()
        font2.setPointSize(12)
        self.profile_fio.setFont(font2)
        self.profile_layout.addWidget(self.profile_fio)

        self.profile_email = QtWidgets.QLabel(
            "E-mail: ", self.profile_tab)
        self.profile_layout.addWidget(self.profile_email)

        self.profile_phone = QtWidgets.QLabel(
            "Телефон: ", self.profile_tab)
        self.profile_layout.addWidget(self.profile_phone)

        self.profile_orders_count = QtWidgets.QLabel(
            "Заказов: 0", self.profile_tab)
        self.profile_layout.addWidget(self.profile_orders_count)

        self.addresses_header = QtWidgets.QLabel(
            "Сохранённые адреса доставки:", self.profile_tab)
        font3 = QtGui.QFont()
        font3.setBold(True)
        self.addresses_header.setFont(font3)
        self.profile_layout.addWidget(self.addresses_header)

        self.addresses_list = QtWidgets.QListWidget(self.profile_tab)
        self.profile_layout.addWidget(self.addresses_list)

        self.address_add_layout = QtWidgets.QHBoxLayout()
        self.new_address_edit = QtWidgets.QLineEdit(self.profile_tab)
        self.new_address_edit.setPlaceholderText("Новый адрес доставки")
        self.new_address_edit.setMinimumHeight(34)
        self.address_add_layout.addWidget(self.new_address_edit)

        self.add_address_btn = QtWidgets.QPushButton(
            "Добавить адрес", self.profile_tab)
        self.add_address_btn.setMinimumHeight(34)
        self.address_add_layout.addWidget(self.add_address_btn)

        self.profile_layout.addLayout(self.address_add_layout)
        self.profile_layout.addStretch()

        self.tabs.addTab(self.profile_tab, "Профиль")

        self.mainLayout.addWidget(self.tabs)

        self.retranslateUi(BuyerForm)
        QtCore.QMetaObject.connectSlotsByName(BuyerForm)

    def retranslateUi(self, BuyerForm):
        _translate = QtCore.QCoreApplication.translate
        BuyerForm.setWindowTitle(
            _translate("BuyerForm", "Аптека — Личный кабинет"))
