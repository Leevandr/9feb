"""Форма добавления / редактирования заказа."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QMessageBox,
    QFormLayout, QCheckBox
)
from PyQt6.QtCore import QDate

from models.db_manager import add_order, update_order


class OrderForm(QWidget):
    def __init__(self, parent_window, order=None):
        super().__init__()
        self.parent_window = parent_window
        self.order = order
        self.is_edit = order is not None

        title = 'Редактирование заказа' if self.is_edit else 'Добавление заказа'
        self.setWindowTitle(title)
        self.setFixedSize(450, 350)
        self._build_ui()

        if self.is_edit:
            self._fill_from_order()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)

        # Артикул (ID)
        if self.is_edit:
            self.id_label = QLabel(str(self.order['OrderID']))
            self.id_label.setStyleSheet(
                'font-weight: bold; color: #7F8C8D;')
            form.addRow('Артикул:', self.id_label)

        # Статус
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            'Новый', 'В обработке', 'Выдан', 'Отменён'])
        form.addRow('Статус:', self.status_combo)

        # Адрес пункта выдачи
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText('Адрес пункта выдачи')
        form.addRow('Адрес:', self.address_edit)

        # Дата заказа
        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())
        form.addRow('Дата заказа:', self.order_date_edit)

        # Дата выдачи
        issue_layout = QHBoxLayout()
        self.issue_date_check = QCheckBox('Указать')
        self.issue_date_check.toggled.connect(self._toggle_issue_date)
        issue_layout.addWidget(self.issue_date_check)

        self.issue_date_edit = QDateEdit()
        self.issue_date_edit.setCalendarPopup(True)
        self.issue_date_edit.setDate(QDate.currentDate())
        self.issue_date_edit.setEnabled(False)
        issue_layout.addWidget(self.issue_date_edit)

        form.addRow('Дата выдачи:', issue_layout)

        layout.addLayout(form)
        layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton('Сохранить')
        save_btn.setStyleSheet(
            'background: #27AE60; color: white; border: none; '
            'border-radius: 6px; padding: 8px 20px; font-weight: bold;')
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _toggle_issue_date(self, checked):
        self.issue_date_edit.setEnabled(checked)

    def _fill_from_order(self):
        """Заполняет поля формы данными заказа."""
        o = self.order

        idx = self.status_combo.findText(o['Status'])
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        self.address_edit.setText(o['DeliveryAddress'])

        if o['OrderDate']:
            date = QDate.fromString(o['OrderDate'], 'yyyy-MM-dd')
            if date.isValid():
                self.order_date_edit.setDate(date)

        if o['IssueDate']:
            self.issue_date_check.setChecked(True)
            date = QDate.fromString(o['IssueDate'], 'yyyy-MM-dd')
            if date.isValid():
                self.issue_date_edit.setDate(date)

    def save(self):
        address = self.address_edit.text().strip()
        if not address:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Адрес пункта выдачи" не может быть пустым.')
            return

        status = self.status_combo.currentText()
        order_date = self.order_date_edit.date().toString('yyyy-MM-dd')

        issue_date = None
        if self.issue_date_check.isChecked():
            issue_date = self.issue_date_edit.date().toString('yyyy-MM-dd')

        data = {
            'UserID': 1,
            'Status': status,
            'DeliveryAddress': address,
            'OrderDate': order_date,
            'IssueDate': issue_date,
        }

        try:
            if self.is_edit:
                update_order(self.order['OrderID'], data)
                QMessageBox.information(
                    self, 'Успех', 'Заказ успешно обновлён.')
            else:
                add_order(data)
                QMessageBox.information(
                    self, 'Успех', 'Заказ успешно добавлен.')

            self.parent_window.refresh_orders()
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self, 'Ошибка сохранения',
                f'Не удалось сохранить заказ:\n{str(e)}')
