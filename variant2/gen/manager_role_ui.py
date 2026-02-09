from PyQt6 import QtWidgets


class Ui_ManagerRoleForm(object):
    def setupUi(self, Form):
        Form.setObjectName("ManagerRoleForm")
        Form.resize(900, 600)
        Form.setWindowTitle("Окно менеджера")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.tabs = QtWidgets.QTabWidget(Form)
        self.mainLayout.addWidget(self.tabs)

        # === Вкладка "Товары" ===
        self.products_tab = QtWidgets.QWidget()
        self.products_layout = QtWidgets.QVBoxLayout(self.products_tab)

        self.product_table = QtWidgets.QTableWidget(self.products_tab)
        self.products_layout.addWidget(self.product_table)

        self.form_layout = QtWidgets.QHBoxLayout()
        self.name_edit = QtWidgets.QLineEdit(self.products_tab)
        self.name_edit.setPlaceholderText("Наименование")
        self.form_layout.addWidget(self.name_edit)
        self.article_edit = QtWidgets.QLineEdit(self.products_tab)
        self.article_edit.setPlaceholderText("Артикул")
        self.form_layout.addWidget(self.article_edit)
        self.category_edit = QtWidgets.QLineEdit(self.products_tab)
        self.category_edit.setPlaceholderText("Категория")
        self.form_layout.addWidget(self.category_edit)
        self.price_edit = QtWidgets.QLineEdit(self.products_tab)
        self.price_edit.setPlaceholderText("Цена")
        self.form_layout.addWidget(self.price_edit)
        self.desc_edit = QtWidgets.QLineEdit(self.products_tab)
        self.desc_edit.setPlaceholderText("Описание")
        self.form_layout.addWidget(self.desc_edit)
        self.photo_edit = QtWidgets.QLineEdit(self.products_tab)
        self.photo_edit.setPlaceholderText("Фото")
        self.form_layout.addWidget(self.photo_edit)
        self.products_layout.addLayout(self.form_layout)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Добавить", self.products_tab)
        self.btn_layout.addWidget(self.add_btn)
        self.edit_btn = QtWidgets.QPushButton("Сохранить", self.products_tab)
        self.btn_layout.addWidget(self.edit_btn)
        self.delete_btn = QtWidgets.QPushButton("Удалить", self.products_tab)
        self.btn_layout.addWidget(self.delete_btn)
        self.products_layout.addLayout(self.btn_layout)

        self.tabs.addTab(self.products_tab, "Товары")

        # === Вкладка "Заказы" ===
        self.orders_tab = QtWidgets.QWidget()
        self.orders_layout = QtWidgets.QVBoxLayout(self.orders_tab)
        self.orders_table = QtWidgets.QTableWidget(self.orders_tab)
        self.orders_layout.addWidget(self.orders_table)

        self.orders_btn_layout = QtWidgets.QHBoxLayout()
        self.accept_btn = QtWidgets.QPushButton("Принять заказ", self.orders_tab)
        self.orders_btn_layout.addWidget(self.accept_btn)
        self.complete_btn = QtWidgets.QPushButton("Выполнен", self.orders_tab)
        self.orders_btn_layout.addWidget(self.complete_btn)
        self.cancel_btn = QtWidgets.QPushButton("Отменить", self.orders_tab)
        self.orders_btn_layout.addWidget(self.cancel_btn)
        self.orders_layout.addLayout(self.orders_btn_layout)

        self.tabs.addTab(self.orders_tab, "Заказы")
