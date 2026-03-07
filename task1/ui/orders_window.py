"""Окно списка заказов."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt

from gen.orders_ui import Ui_OrdersForm
from models.db_manager import load_orders, delete_order


class OrdersWindow(QWidget):
    def __init__(self, role, parent_window):
        super().__init__()
        self.role = role
        self.parent_window = parent_window
        self.order_form = None

        self.ui = Ui_OrdersForm()
        self.ui.setupUi(self)

        self.setWindowTitle('Заказы')
        self.resize(700, 500)

        # Скрыть кнопки для менеджера
        if self.role != 'admin':
            self.ui.add_btn.setVisible(False)
            self.ui.delete_btn.setVisible(False)

        # Подключение сигналов
        self.ui.back_btn.clicked.connect(self.close)

        if self.role == 'admin':
            self.ui.add_btn.clicked.connect(self.open_add_order)
            self.ui.delete_btn.clicked.connect(
                self.delete_selected_order)

        self.refresh_orders()

    def refresh_orders(self):
        """Перезагружает список заказов."""
        layout = self.ui.cards_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        orders = load_orders()
        for order in orders:
            card = self._create_order_card(order)
            layout.addWidget(card)

        layout.addStretch()

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

        # Артикул
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
        date_label.setStyleSheet(
            'font-size: 12px; color: #7F8C8D;')
        left_info.addWidget(date_label)
        bottom_layout.addLayout(left_info)

        bottom_layout.addStretch()

        issue_date = order['IssueDate'] or '—'
        issue_label = QLabel(f'Дата доставки:\n{issue_date}')
        issue_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        issue_label.setStyleSheet(
            'font-size: 12px; color: #7F8C8D;')
        bottom_layout.addWidget(issue_label)

        card_layout.addLayout(bottom_layout)

        # Клик для админа — редактирование
        if self.role == 'admin':
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = (
                lambda event, o=order: self.open_edit_order(o))

        return card

    def open_add_order(self):
        if self.order_form is not None \
                and self.order_form.isVisible():
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
        if self.order_form is not None \
                and self.order_form.isVisible():
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
        orders = load_orders()
        items = [
            f'#{o["OrderID"]}: {o["Status"]} — '
            f'{o["DeliveryAddress"]}'
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
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            delete_order(order_id)
            self.refresh_orders()
            QMessageBox.information(
                self, 'Успех',
                f'Заказ #{order_id} удалён.')
