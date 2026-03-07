from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox,
    QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt


class Ui_ProductForm:
    def setupUi(self, widget):
        self.main_layout = QVBoxLayout(widget)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(8)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(8)

        # ID
        self.id_text_label = QLabel('ID товара:')
        self.id_label = QLabel()
        self.id_label.setStyleSheet(
            'font-weight: bold; color: #7F8C8D;')
        self.form_layout.addRow(self.id_text_label, self.id_label)

        # Наименование
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Наименование товара')
        self.form_layout.addRow('Наименование:', self.name_edit)

        # Категория
        self.category_combo = QComboBox()
        self.form_layout.addRow('Категория:', self.category_combo)

        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText('Описание товара')
        self.form_layout.addRow('Описание:', self.description_edit)

        # Производитель
        self.manufacturer_combo = QComboBox()
        self.form_layout.addRow('Производитель:',
                                self.manufacturer_combo)

        # Поставщик
        self.supplier_combo = QComboBox()
        self.form_layout.addRow('Поставщик:', self.supplier_combo)

        # Цена
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(' руб.')
        self.form_layout.addRow('Цена:', self.price_spin)

        # Единица измерения
        self.unit_edit = QLineEdit()
        self.unit_edit.setText('шт')
        self.form_layout.addRow('Ед. изм.:', self.unit_edit)

        # Количество на складе
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 999999)
        self.form_layout.addRow('На складе:', self.stock_spin)

        # Скидка
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix('%')
        self.form_layout.addRow('Скидка:', self.discount_spin)

        self.main_layout.addLayout(self.form_layout)

        # Фото
        self.photo_layout = QHBoxLayout()

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 100)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet(
            'border: 1px solid #D5D8DC; border-radius: 6px;')
        self.photo_layout.addWidget(self.photo_label)

        photo_btn_layout = QVBoxLayout()
        self.upload_btn = QPushButton('Загрузить фото')
        photo_btn_layout.addWidget(self.upload_btn)
        photo_btn_layout.addStretch()
        self.photo_layout.addLayout(photo_btn_layout)
        self.photo_layout.addStretch()

        self.main_layout.addLayout(self.photo_layout)

        # Кнопки
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()

        self.cancel_btn = QPushButton('Отмена')
        self.buttons_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton('Сохранить')
        self.save_btn.setObjectName('save_btn')
        self.save_btn.setStyleSheet(
            'background: #27AE60; color: white; border: none; '
            'border-radius: 6px; padding: 8px 20px; font-weight: bold;')
        self.buttons_layout.addWidget(self.save_btn)

        self.main_layout.addLayout(self.buttons_layout)
