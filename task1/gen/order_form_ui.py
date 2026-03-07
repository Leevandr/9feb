from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QCheckBox, QPushButton,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QDate


class Ui_OrderForm:
    def setupUi(self, widget):
        self.main_layout = QVBoxLayout(widget)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(10)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(10)

        # Артикул
        self.id_text_label = QLabel('Артикул:')
        self.id_label = QLabel()
        self.id_label.setStyleSheet(
            'font-weight: bold; color: #7F8C8D;')
        self.form_layout.addRow(self.id_text_label, self.id_label)

        # Статус
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            'Новый', 'В обработке', 'Выдан', 'Отменён'])
        self.form_layout.addRow('Статус:', self.status_combo)

        # Адрес
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText('Адрес пункта выдачи')
        self.form_layout.addRow('Адрес:', self.address_edit)

        # Дата заказа
        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())
        self.form_layout.addRow('Дата заказа:', self.order_date_edit)

        # Дата выдачи
        issue_layout = QHBoxLayout()
        self.issue_date_check = QCheckBox('Указать')
        issue_layout.addWidget(self.issue_date_check)

        self.issue_date_edit = QDateEdit()
        self.issue_date_edit.setCalendarPopup(True)
        self.issue_date_edit.setDate(QDate.currentDate())
        self.issue_date_edit.setEnabled(False)
        issue_layout.addWidget(self.issue_date_edit)

        self.form_layout.addRow('Дата выдачи:', issue_layout)

        self.main_layout.addLayout(self.form_layout)

        self.main_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding))

        # Кнопки
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()

        self.cancel_btn = QPushButton('Отмена')
        self.buttons_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton('Сохранить')
        self.save_btn.setStyleSheet(
            'background: #27AE60; color: white; border: none; '
            'border-radius: 6px; padding: 8px 20px; font-weight: bold;')
        self.buttons_layout.addWidget(self.save_btn)

        self.main_layout.addLayout(self.buttons_layout)
