from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QDate

from gen.order_form_ui import Ui_OrderFormUI as Ui_OrderForm
from models.db_manager import add_order, update_order


class OrderForm(QWidget):
    def __init__(self, parent_window, order=None):
        super().__init__()
        self.parent_window = parent_window
        self.order = order
        self.is_edit = order is not None

        self.ui = Ui_OrderForm()
        self.ui.setupUi(self)

        title = 'Редактирование заказа' if self.is_edit \
            else 'Добавление заказа'
        self.setWindowTitle(title)
        self.setFixedSize(450, 350)

        if not self.is_edit:
            self.ui.id_text_label.setVisible(False)
            self.ui.id_label.setVisible(False)

        self.ui.issue_date_check.toggled.connect(
            self.ui.issue_date_edit.setEnabled)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.save_btn.clicked.connect(self.save)

        if self.is_edit:
            self._fill_from_order()

    def _fill_from_order(self):
        o = self.order
        self.ui.id_label.setText(str(o['OrderID']))

        idx = self.ui.status_combo.findText(o['Status'])
        if idx >= 0:
            self.ui.status_combo.setCurrentIndex(idx)

        self.ui.address_edit.setText(o['DeliveryAddress'])

        if o['OrderDate']:
            date = QDate.fromString(o['OrderDate'], 'yyyy-MM-dd')
            if date.isValid():
                self.ui.order_date_edit.setDate(date)

        if o['IssueDate']:
            self.ui.issue_date_check.setChecked(True)
            date = QDate.fromString(o['IssueDate'], 'yyyy-MM-dd')
            if date.isValid():
                self.ui.issue_date_edit.setDate(date)

    def save(self):
        address = self.ui.address_edit.text().strip()
        if not address:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Адрес пункта выдачи" не может быть пустым.')
            return

        status = self.ui.status_combo.currentText()
        order_date = self.ui.order_date_edit.date().toString(
            'yyyy-MM-dd')

        issue_date = None
        if self.ui.issue_date_check.isChecked():
            issue_date = self.ui.issue_date_edit.date().toString(
                'yyyy-MM-dd')

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
