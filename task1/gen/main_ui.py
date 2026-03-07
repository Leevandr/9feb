from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QScrollArea, QWidget,
    QSpacerItem, QSizePolicy
)


class Ui_MainForm:
    def setupUi(self, widget):
        self.main_layout = QVBoxLayout(widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # Верхняя панель
        self.top_panel = QHBoxLayout()

        self.logo_label = QLabel()
        self.top_panel.addWidget(self.logo_label)

        self.top_panel.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Minimum))

        self.fio_label = QLabel()
        self.fio_label.setStyleSheet(
            'font-weight: bold; font-size: 13px; color: #2C3E50;')
        self.top_panel.addWidget(self.fio_label)

        self.orders_btn = QPushButton('Заказы')
        self.top_panel.addWidget(self.orders_btn)

        self.add_product_btn = QPushButton('Добавить товар')
        self.add_product_btn.setObjectName('add_btn')
        self.top_panel.addWidget(self.add_product_btn)

        self.logout_btn = QPushButton('Выход')
        self.top_panel.addWidget(self.logout_btn)

        self.main_layout.addLayout(self.top_panel)

        # Панель фильтров
        self.filter_panel = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            'Поиск по названию, описанию, производителю...')
        self.filter_panel.addWidget(self.search_edit)

        self.supplier_combo = QComboBox()
        self.filter_panel.addWidget(self.supplier_combo)

        self.sort_combo = QComboBox()
        self.filter_panel.addWidget(self.sort_combo)

        self.main_layout.addLayout(self.filter_panel)

        # Счётчик
        self.count_label = QLabel()
        self.count_label.setStyleSheet(
            'color: #7F8C8D; font-size: 12px;')
        self.main_layout.addWidget(self.count_label)

        # Панель действий
        self.action_panel = QHBoxLayout()
        self.action_panel.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Minimum))

        self.delete_btn = QPushButton('Удалить выбранный товар')
        self.delete_btn.setObjectName('delete_btn')
        self.delete_btn.setStyleSheet(
            'background: #E74C3C; color: white; '
            'border: none; border-radius: 6px; padding: 6px 14px;')
        self.action_panel.addWidget(self.delete_btn)

        self.main_layout.addLayout(self.action_panel)

        # Область прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('QScrollArea { border: none; }')

        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
