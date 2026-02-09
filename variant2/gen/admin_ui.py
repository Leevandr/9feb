from PyQt6 import QtWidgets


class Ui_AdminForm(object):
    def setupUi(self, Form):
        Form.setObjectName("AdminForm")
        Form.resize(800, 550)
        Form.setWindowTitle("Окно администратора")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.tabs = QtWidgets.QTabWidget(Form)
        self.mainLayout.addWidget(self.tabs)

        # === Вкладка "Пользователи" ===
        self.users_tab = QtWidgets.QWidget()
        self.users_layout = QtWidgets.QVBoxLayout(self.users_tab)
        self.users_table = QtWidgets.QTableWidget(self.users_tab)
        self.users_layout.addWidget(self.users_table)

        self.user_form_layout = QtWidgets.QHBoxLayout()
        self.login_edit = QtWidgets.QLineEdit(self.users_tab)
        self.login_edit.setPlaceholderText("Логин")
        self.user_form_layout.addWidget(self.login_edit)
        self.password_input = QtWidgets.QLineEdit(self.users_tab)
        self.password_input.setPlaceholderText("Пароль")
        self.user_form_layout.addWidget(self.password_input)
        self.role_combo = QtWidgets.QComboBox(self.users_tab)
        self.role_combo.addItems(["buyer", "manager", "admin"])
        self.user_form_layout.addWidget(self.role_combo)
        self.users_layout.addLayout(self.user_form_layout)

        self.user_btn_layout = QtWidgets.QHBoxLayout()
        self.add_user_btn = QtWidgets.QPushButton("Добавить", self.users_tab)
        self.user_btn_layout.addWidget(self.add_user_btn)
        self.delete_user_btn = QtWidgets.QPushButton("Удалить", self.users_tab)
        self.user_btn_layout.addWidget(self.delete_user_btn)
        self.users_layout.addLayout(self.user_btn_layout)

        self.tabs.addTab(self.users_tab, "Пользователи")

        # === Вкладка "Статистика продаж" ===
        self.stats_tab = QtWidgets.QWidget()
        self.stats_layout = QtWidgets.QVBoxLayout(self.stats_tab)

        self.total_orders_label = QtWidgets.QLabel("Всего заказов: 0", self.stats_tab)
        self.stats_layout.addWidget(self.total_orders_label)
        self.total_revenue_label = QtWidgets.QLabel("Общая выручка: 0", self.stats_tab)
        self.stats_layout.addWidget(self.total_revenue_label)

        self.stats_table = QtWidgets.QTableWidget(self.stats_tab)
        self.stats_layout.addWidget(self.stats_table)

        self.tabs.addTab(self.stats_tab, "Статистика продаж")
