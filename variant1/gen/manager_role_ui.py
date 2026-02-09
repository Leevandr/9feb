from PyQt6 import QtWidgets


class Ui_ManagerRoleForm(object):
    def setupUi(self, Form):
        Form.setObjectName("ManagerRoleForm")
        Form.resize(700, 500)
        Form.setWindowTitle("Окно руководителя")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.tabs = QtWidgets.QTabWidget(Form)
        self.mainLayout.addWidget(self.tabs)

        # === Вкладка "Статистика" ===
        self.stats_tab = QtWidgets.QWidget()
        self.stats_layout = QtWidgets.QVBoxLayout(self.stats_tab)

        self.total_label = QtWidgets.QLabel("Всего книг: 0", self.stats_tab)
        self.stats_layout.addWidget(self.total_label)

        self.genre_label = QtWidgets.QLabel("По жанрам:", self.stats_tab)
        self.stats_layout.addWidget(self.genre_label)
        self.genre_table = QtWidgets.QTableWidget(self.stats_tab)
        self.stats_layout.addWidget(self.genre_table)

        self.author_label = QtWidgets.QLabel("По авторам:", self.stats_tab)
        self.stats_layout.addWidget(self.author_label)
        self.author_table = QtWidgets.QTableWidget(self.stats_tab)
        self.stats_layout.addWidget(self.author_table)

        self.tabs.addTab(self.stats_tab, "Статистика")

        # === Вкладка "Доп. материалы" ===
        self.materials_tab = QtWidgets.QWidget()
        self.mat_layout = QtWidgets.QVBoxLayout(self.materials_tab)
        self.mat_table = QtWidgets.QTableWidget(self.materials_tab)
        self.mat_layout.addWidget(self.mat_table)
        self.tabs.addTab(self.materials_tab, "Доп. материалы")
