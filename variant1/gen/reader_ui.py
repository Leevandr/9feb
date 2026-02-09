from PyQt6 import QtWidgets


class Ui_ReaderForm(object):
    def setupUi(self, Form):
        Form.setObjectName("ReaderForm")
        Form.resize(850, 600)
        Form.setWindowTitle("Окно читателя")

        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.tabs = QtWidgets.QTabWidget(Form)
        self.mainLayout.addWidget(self.tabs)

        # === Вкладка "Поиск" ===
        self.search_tab = QtWidgets.QWidget()
        self.search_layout = QtWidgets.QVBoxLayout(self.search_tab)

        self.filter_layout = QtWidgets.QHBoxLayout()
        self.author_edit = QtWidgets.QLineEdit(self.search_tab)
        self.author_edit.setPlaceholderText("Автор")
        self.filter_layout.addWidget(self.author_edit)
        self.genre_combo = QtWidgets.QComboBox(self.search_tab)
        self.filter_layout.addWidget(self.genre_combo)
        self.search_btn = QtWidgets.QPushButton("Искать", self.search_tab)
        self.filter_layout.addWidget(self.search_btn)
        self.reset_btn = QtWidgets.QPushButton("Сброс", self.search_tab)
        self.filter_layout.addWidget(self.reset_btn)
        self.search_layout.addLayout(self.filter_layout)

        self.table = QtWidgets.QTableWidget(self.search_tab)
        self.search_layout.addWidget(self.table)

        self.tabs.addTab(self.search_tab, "Поиск")

        # === Вкладка "Чтение" ===
        self.reading_tab = QtWidgets.QWidget()
        self.reading_layout = QtWidgets.QVBoxLayout(self.reading_tab)
        self.book_title_label = QtWidgets.QLabel("Выберите книгу в таблице и нажмите 'Читать'",
                                                  self.reading_tab)
        self.reading_layout.addWidget(self.book_title_label)
        self.read_btn = QtWidgets.QPushButton("Читать выбранную книгу", self.reading_tab)
        self.reading_layout.addWidget(self.read_btn)
        self.text_edit = QtWidgets.QTextEdit(self.reading_tab)
        self.text_edit.setReadOnly(True)
        self.reading_layout.addWidget(self.text_edit)
        self.tabs.addTab(self.reading_tab, "Чтение")

        # === Вкладка "Подписки" ===
        self.sub_tab = QtWidgets.QWidget()
        self.sub_layout = QtWidgets.QVBoxLayout(self.sub_tab)

        self.sub_h_layout = QtWidgets.QHBoxLayout()
        self.sub_genre_combo = QtWidgets.QComboBox(self.sub_tab)
        self.sub_h_layout.addWidget(self.sub_genre_combo)
        self.subscribe_btn = QtWidgets.QPushButton("Подписаться", self.sub_tab)
        self.sub_h_layout.addWidget(self.subscribe_btn)
        self.unsubscribe_btn = QtWidgets.QPushButton("Отписаться", self.sub_tab)
        self.sub_h_layout.addWidget(self.unsubscribe_btn)
        self.sub_layout.addLayout(self.sub_h_layout)

        self.sub_list = QtWidgets.QListWidget(self.sub_tab)
        self.sub_layout.addWidget(self.sub_list)
        self.tabs.addTab(self.sub_tab, "Подписки")
