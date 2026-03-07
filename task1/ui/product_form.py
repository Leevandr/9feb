"""Форма добавления / редактирования товара."""
import os

from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from gen.product_form_ui import Ui_ProductForm
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

        self.ui = Ui_ProductForm()
        self.ui.setupUi(self)

        title = 'Редактирование товара' if self.is_edit \
            else 'Добавление товара'
        self.setWindowTitle(title)
        self.setFixedSize(500, 650)

        # Заполнение комбобоксов
        self.categories = load_categories()
        for c in self.categories:
            self.ui.category_combo.addItem(
                c['Name'], c['CategoryID'])

        self.manufacturers = load_manufacturers()
        for m in self.manufacturers:
            self.ui.manufacturer_combo.addItem(
                m['Name'], m['ManufacturerID'])

        self.suppliers = load_suppliers()
        for s in self.suppliers:
            self.ui.supplier_combo.addItem(
                s['Name'], s['SupplierID'])

        # Скрыть ID при добавлении
        if not self.is_edit:
            self.ui.id_text_label.setVisible(False)
            self.ui.id_label.setVisible(False)

        # Подключение сигналов
        self.ui.upload_btn.clicked.connect(self.browse_photo)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.save_btn.clicked.connect(self.save)

        if self.is_edit:
            self._fill_from_product()

        self._update_photo_preview()

    def _fill_from_product(self):
        """Заполняет поля формы данными товара."""
        p = self.product
        self.ui.id_label.setText(str(p['ProductID']))
        self.ui.name_edit.setText(p['Name'])

        idx = self.ui.category_combo.findData(p['CategoryID'])
        if idx >= 0:
            self.ui.category_combo.setCurrentIndex(idx)

        self.ui.description_edit.setPlainText(
            p.get('Description', '') or '')

        idx = self.ui.manufacturer_combo.findData(p['ManufacturerID'])
        if idx >= 0:
            self.ui.manufacturer_combo.setCurrentIndex(idx)

        idx = self.ui.supplier_combo.findData(p['SupplierID'])
        if idx >= 0:
            self.ui.supplier_combo.setCurrentIndex(idx)

        self.ui.price_spin.setValue(p['Price'])
        self.ui.unit_edit.setText(p['Unit'])
        self.ui.stock_spin.setValue(p['StockQuantity'])
        self.ui.discount_spin.setValue(p['Discount'])

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
            self.ui.photo_label.setPixmap(pix)

    def browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите изображение', '',
            'Изображения (*.png *.jpg *.jpeg *.bmp)')
        if path:
            self.new_image_path = path
            self._update_photo_preview()

    def save(self):
        name = self.ui.name_edit.text().strip()
        if not name:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Наименование" не может быть пустым.')
            return

        unit = self.ui.unit_edit.text().strip()
        if not unit:
            QMessageBox.warning(
                self, 'Ошибка валидации',
                'Поле "Единица измерения" не может быть пустым.')
            return

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

            # Масштабируем до 300x200 и сохраняем
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
            'CategoryID': self.ui.category_combo.currentData(),
            'Description':
                self.ui.description_edit.toPlainText().strip(),
            'ManufacturerID':
                self.ui.manufacturer_combo.currentData(),
            'SupplierID': self.ui.supplier_combo.currentData(),
            'Price': self.ui.price_spin.value(),
            'Unit': unit,
            'StockQuantity': self.ui.stock_spin.value(),
            'Discount': self.ui.discount_spin.value(),
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
