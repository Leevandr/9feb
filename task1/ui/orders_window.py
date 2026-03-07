"""Окно списка заказов."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt

from models.db_manager import load_orders, delete_order


class OrdersWindow(QWidget):
    def __init__(self, role, parent_window):
        super().__init__()
        self.role = role
        self.parent_window = parent_window
        self.order_form = None

        self.setWindowTitle('Заказы')
        self.resize(700, 500)
        self._build_ui()
        self.refresh_orders()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Верхняя панель
        top_panel = QHBoxLayout()

        title = QLabel('Список заказов')
        title.setStyleSheet(
            'font-size: 18px; font-weight: bold; color: #2C3E50;')
        top_panel.addWidget(title)

        top_panel.addStretch()

        if self.role == 'admin':
            add_btn = QPushButton('Добавить заказ')
            add_btn.setStyleSheet(
                'background: #27AE60; color: white; border: none; '
                'border-radius: 6px; padding: 6px 14px; '
                'font-weight: bold;')
            add_btn.clicked.connect(self.open_add_order)
            top_panel.addWidget(add_btn)

            del_btn = QPushButton('Удалить заказ')
            del_btn.setStyleSheet(
                'background: #E74C3C; color: white; border: none; '
                'border-radius: 6px; padding: 6px 14px;')
            del_btn.clicked.connect(self.delete_selected_order)
            top_panel.addWidget(del_btn)

        back_btn = QPushButton('Назад')
        back_btn.clicked.connect(self.close)
        top_panel.addWidget(back_btn)

        layout.addLayout(top_panel)

        # Список заказов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('QScrollArea { border: none; }')

        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

    def refresh_orders(self):
        """Перезагружает список заказов."""
        # Очистка
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        orders = load_orders()
        for order in orders:
            card = self._create_order_card(order)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def _create_order_card(self, order):
        """Создаёт карточку заказа по макету из ТЗ."""
        card = QFrame()
        card.setObjectName('order_card')
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            'QFrame#order_card { background: white; '
            'border: 1px solid #E0E0E0; border-radius: 10px; }')

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)

        # Артикул заказа
        article_label = QLabel(
            f'Артикул заказа: #{order["OrderID"]}')
        article_label.setStyleSheet(
            'font-weight: bold; font-size: 14px; color: #2C3E50;')
        card_layout.addWidget(article_label)

        # Статус
        status = order['Status']
        status_colors = {
            'Новый': '#3498DB',
            'В обработке': '#F39C12',
            'Выдан': '#27AE60',
        }
        color = status_colors.get(status, '#7F8C8D')
        status_label = QLabel(f'Статус: {status}')
        status_label.setStyleSheet(
            f'color: {color}; font-weight: bold; font-size: 13px;')
        card_layout.addWidget(status_label)

        # Адрес и даты
        bottom_layout = QHBoxLayout()

        left_info = QVBoxLayout()
        addr_label = QLabel(
            f'Адрес пункта выдачи: {order["DeliveryAddress"]}')
        addr_label.setWordWrap(True)
        addr_label.setStyleSheet('font-size: 12px;')
        left_info.addWidget(addr_label)

        date_label = QLabel(
            f'Дата заказа: {order["OrderDate"]}')
        date_label.setStyleSheet('font-size: 12px; color: #7F8C8D;')
        left_info.addWidget(date_label)
        bottom_layout.addLayout(left_info)

        bottom_layout.addStretch()

        issue_date = order['IssueDate'] or '—'
        issue_label = QLabel(f'Дата доставки:\n{issue_date}')
        issue_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        issue_label.setStyleSheet('font-size: 12px; color: #7F8C8D;')
        bottom_layout.addWidget(issue_label)

        card_layout.addLayout(bottom_layout)

        # Клик по карточке (админ — редактирование)
        if self.role == 'admin':
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = (
                lambda event, o=order: self.open_edit_order(o))

        return card

    def open_add_order(self):
        if self.order_form is not None and self.order_form.isVisible():
            QMessageBox.information(
                self, 'Внимание',
                'Окно редактирования заказа уже открыто.')
            self.order_form.activateWindow()
            return
        from ui.order_form import OrderForm
        self.order_form = OrderForm(
            parent_window=self, order=None)
        self.order_form.show()

    def open_edit_order(self, order):
        if self.order_form is not None and self.order_form.isVisible():
            QMessageBox.information(
                self, 'Внимание',
                'Окно редактирования заказа уже открыто.')
            self.order_form.activateWindow()
            return
        from ui.order_form import OrderForm
        self.order_form = OrderForm(
            parent_window=self, order=order)
        self.order_form.show()

    def delete_selected_order(self):
        from PyQt6.QtWidgets import QInputDialog
        orders = load_orders()
        items = [
            f'#{o["OrderID"]}: {o["Status"]} — {o["DeliveryAddress"]}'
            for o in orders
        ]
        if not items:
            QMessageBox.information(
                self, 'Информация', 'Нет заказов для удаления.')
            return

        item, ok = QInputDialog.getItem(
            self, 'Удаление заказа',
            'Выберите заказ для удаления:', items, 0, False)
        if not ok:
            return

        order_id = int(item.split(':')[0].replace('#', ''))

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить заказ #{order_id}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            delete_order(order_id)
            self.refresh_orders()
            QMessageBox.information(
                self, 'Успех',
                f'Заказ #{order_id} удалён.')
