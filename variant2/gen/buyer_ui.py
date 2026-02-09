from PyQt6 import QtWidgets


class Ui_BuyerForm(object):
    def setupUi(self, Form):
        Form.setObjectName("BuyerForm")
        Form.resize(850, 600)
        Form.setWindowTitle("Окно покупателя")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.tabs = QtWidgets.QTabWidget(Form)
        self.mainLayout.addWidget(self.tabs)

        # === Вкладка "Каталог" ===
        self.catalog_tab = QtWidgets.QWidget()
        self.catalog_layout = QtWidgets.QVBoxLayout(self.catalog_tab)

        self.filter_layout = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit(self.catalog_tab)
        self.search_edit.setPlaceholderText("Артикул или название")
        self.filter_layout.addWidget(self.search_edit)
        self.category_combo = QtWidgets.QComboBox(self.catalog_tab)
        self.filter_layout.addWidget(self.category_combo)
        self.search_btn = QtWidgets.QPushButton("Искать", self.catalog_tab)
        self.filter_layout.addWidget(self.search_btn)
        self.reset_btn = QtWidgets.QPushButton("Сброс", self.catalog_tab)
        self.filter_layout.addWidget(self.reset_btn)
        self.catalog_layout.addLayout(self.filter_layout)

        self.catalog_table = QtWidgets.QTableWidget(self.catalog_tab)
        self.catalog_layout.addWidget(self.catalog_table)

        self.add_to_cart_btn = QtWidgets.QPushButton("В корзину", self.catalog_tab)
        self.catalog_layout.addWidget(self.add_to_cart_btn)
        self.tabs.addTab(self.catalog_tab, "Каталог")

        # === Вкладка "Корзина" ===
        self.cart_tab = QtWidgets.QWidget()
        self.cart_layout = QtWidgets.QVBoxLayout(self.cart_tab)
        self.cart_table = QtWidgets.QTableWidget(self.cart_tab)
        self.cart_layout.addWidget(self.cart_table)

        self.cart_btn_layout = QtWidgets.QHBoxLayout()
        self.remove_from_cart_btn = QtWidgets.QPushButton("Удалить из корзины",
                                                          self.cart_tab)
        self.cart_btn_layout.addWidget(self.remove_from_cart_btn)
        self.checkout_btn = QtWidgets.QPushButton("Оформить заказ", self.cart_tab)
        self.cart_btn_layout.addWidget(self.checkout_btn)
        self.cart_total_label = QtWidgets.QLabel("Итого: 0", self.cart_tab)
        self.cart_btn_layout.addWidget(self.cart_total_label)
        self.cart_layout.addLayout(self.cart_btn_layout)
        self.tabs.addTab(self.cart_tab, "Корзина")

        # === Вкладка "Заказы" ===
        self.orders_tab = QtWidgets.QWidget()
        self.orders_layout = QtWidgets.QVBoxLayout(self.orders_tab)
        self.orders_table = QtWidgets.QTableWidget(self.orders_tab)
        self.orders_layout.addWidget(self.orders_table)
        self.tabs.addTab(self.orders_tab, "Заказы")

        # === Вкладка "Личный кабинет" ===
        self.profile_tab = QtWidgets.QWidget()
        self.profile_layout = QtWidgets.QVBoxLayout(self.profile_tab)
        self.profile_name = QtWidgets.QLabel("Покупатель: buyer", self.profile_tab)
        self.profile_layout.addWidget(self.profile_name)
        self.profile_orders_count = QtWidgets.QLabel("Заказов: 0", self.profile_tab)
        self.profile_layout.addWidget(self.profile_orders_count)
        self.profile_layout.addStretch()
        self.tabs.addTab(self.profile_tab, "Личный кабинет")
