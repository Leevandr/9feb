from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QSpacerItem, QSizePolicy
)


class Ui_OrdersForm:
    def setupUi(self, widget):
        self.main_layout = QVBoxLayout(widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # Верхняя панель
        self.top_panel = QHBoxLayout()

        self.title_label = QLabel('Список заказов')
        self.title_label.setStyleSheet(
            'font-size: 18px; font-weight: bold; color: #2C3E50;')
        self.top_panel.addWidget(self.title_label)

        self.top_panel.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Minimum))

        self.add_btn = QPushButton('Добавить заказ')
        self.add_btn.setStyleSheet(
            'background: #27AE60; color: white; border: none; '
            'border-radius: 6px; padding: 6px 14px; font-weight: bold;')
        self.top_panel.addWidget(self.add_btn)

        self.delete_btn = QPushButton('Удалить заказ')
        self.delete_btn.setStyleSheet(
            'background: #E74C3C; color: white; border: none; '
            'border-radius: 6px; padding: 6px 14px;')
        self.top_panel.addWidget(self.delete_btn)

        self.back_btn = QPushButton('Назад')
        self.top_panel.addWidget(self.back_btn)

        self.main_layout.addLayout(self.top_panel)

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
