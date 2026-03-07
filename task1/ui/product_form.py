"""Форма добавления / редактирования товара."""
import os
import shutil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox,
    QPushButton, QMessageBox, QFileDialog, QFormLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from models.db_manager import (
    load_categories, load_manufacturers, load_suppliers,
    add_product, update_product
)
from utils.helpers import get_image_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ProductForm(QWidget):
    def __init__(self, parent_window, product=None):
        super().__init__()
        self.parent_window = parent_window
        self.product = product
        self.is_edit = product is not None
        self.new_image_path = None

        title = 'Редактирование товара' if self.is_edit else 'Добавление товара'
        self.setWindowTitle(title)
        self.setFixedSize(500, 650)
        self._build_ui()

        if self.is_edit:
            self._fill_from_product()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(8)

        # ID (только при редактировании)
        if self.is_edit:
            self.id_label = QLabel(str(self.product['ProductID']))
            self.id_label.setStyleSheet(
                'font-weight: bold; color: #7F8C8D;')
            form.addRow('ID товара:', self.id_label)

        # Наименование
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Наименование товара')
        form.addRow('Наименование:', self.name_edit)

        # Категория
        self.category_combo = QComboBox()
        self.categories = load_categories()
        for c in self.categories:
            self.category_combo.addItem(c['Name'], c['CategoryID'])
        form.addRow('Категория:', self.category_combo)

        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText('Описание товара')
        form.addRow('Описание:', self.description_edit)

        # Производитель
        self.manufacturer_combo = QComboBox()
        self.manufacturers = load_manufacturers()
        for m in self.manufacturers:
            self.manufacturer_combo.addItem(
                m['Name'], m['ManufacturerID'])
        form.addRow('Производитель:', self.manufacturer_combo)

        # Поставщик
        self.supplier_combo = QComboBox()
        self.suppliers = load_suppliers()
        for s in self.suppliers:
            self.supplier_combo.addItem(s['Name'], s['SupplierID'])
        form.addRow('Поставщик:', self.supplier_combo)

        # Цена
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(' руб.')
        form.addRow('Цена:', self.price_spin)

        # Единица измерения
        self.unit_edit = QLineEdit()
        self.unit_edit.setText('шт')
        form.addRow('Ед. изм.:', self.unit_edit)

        # Количество на складе
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 999999)
        form.addRow('На складе:', self.stock_spin)

        # Скидка
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix('%')
        form.addRow('Скидка:', self.discount_spin)

        layout.addLayout(form)

        # Фото
        photo_layout = QHBoxLayout()

        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 100)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet(
            'border: 1px solid #D5D8DC; border-radius: 6px;')
        photo_layout.addWidget(self.photo_label)

        photo_btn_layout = QVBoxLayout()
        self.upload_btn = QPushButton('Загрузить фото')
        self.upload_btn.clicked.connect(self.browse_photo)
        photo_btn_layout.addWidget(self.upload_btn)
        photo_btn_layout.addStretch()
        photo_layout.addLayout(photo_btn_layout)
        photo_layout.addStretch()

        layout.addLayout(photo_layout)

        self._update_photo_preview()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton('Сохранить')
        save_btn.setObjectName('save_btn')
        save_btn.setStyleSheet(
            'background: #27AE60; color: white; border: none; '
            'border-radius: 6px; padding: 8px 20px; font-weight: bold;')
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _fill_from_product(self):
        """Заполняет поля формы данными товара."""
        p = self.product
        self.name_edit.setText(p['Name'])

        # Категория
        idx = self.category_combo.findData(p['CategoryID'])
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)

        self.description_edit.setPlainText(p.get('Description', ''))

        # Производитель
        idx = self.manufacturer_combo.findData(p['ManufacturerID'])
        if idx >= 0:
            self.manufacturer_combo.setCurrentIndex(idx)

        # Поставщик
        idx = self.supplier_combo.findData(p['SupplierID'])
        if idx >= 0:
            self.supplier_combo.setCurrentIndex(idx)

        self.price_spin.setValue(p['Price'])
        self.unit_edit.setText(p['Unit'])
        self.stock_spin.setValue(p['StockQuantity'])
        self.discount_spin.setValue(p['Discount'])

        self._update_photo_preview()

    def _update_photo_preview(self):
        """Обновляет превью фото."""
        if self.new_image_path:
            path = self.new_image_path
        elif self.is_edit and self.product.get('ImagePath'):
            path = get_image_path(self.product['ImagePath'])
        else:
            path = get_image_path(None)

        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaled(
                150, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.photo_label.setPixmap(pix)

    def browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите изображение', '',
            'Изображения (*.png *.jpg *.jpeg *.bmp)')
        if path:
            self.new_image_path = path
            self._update_photo_preview()

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Наименование" не может быть пустым.')
            return

        unit = self.unit_edit.text().strip()
        if not unit:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Единица измерения" не может быть пустым.')
            return

        price = self.price_spin.value()
        stock = self.stock_spin.value()
        discount = self.discount_spin.value()

        # Обработка изображения
        image_path = None
        if self.is_edit:
            image_path = self.product.get('ImagePath')

        if self.new_image_path:
            images_dir = os.path.join(BASE_DIR, 'images')
            os.makedirs(images_dir, exist_ok=True)

            # Удаляем старое фото при замене
            if self.is_edit and self.product.get('ImagePath'):
                old_path = os.path.join(
                    BASE_DIR, self.product['ImagePath'])
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Масштабируем и сохраняем новое фото
            ext = os.path.splitext(self.new_image_path)[1]
            filename = f'{name.replace(" ", "_").lower()}{ext}'
            dest_path = os.path.join(images_dir, filename)

            pix = QPixmap(self.new_image_path)
            pix = pix.scaled(
                300, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            pix.save(dest_path)

            image_path = f'images/{filename}'

        data = {
            'Name': name,
            'CategoryID': self.category_combo.currentData(),
            'Description': self.description_edit.toPlainText().strip(),
            'ManufacturerID': self.manufacturer_combo.currentData(),
            'SupplierID': self.supplier_combo.currentData(),
            'Price': price,
            'Unit': unit,
            'StockQuantity': stock,
            'Discount': discount,
            'ImagePath': image_path,
        }

        try:
            if self.is_edit:
                update_product(self.product['ProductID'], data)
                QMessageBox.information(
                    self, 'Успех', 'Товар успешно обновлён.')
            else:
                add_product(data)
                QMessageBox.information(
                    self, 'Успех', 'Товар успешно добавлен.')

            self.parent_window.refresh_products()
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self, 'Ошибка сохранения',
                f'Не удалось сохранить товар:\n{str(e)}')
