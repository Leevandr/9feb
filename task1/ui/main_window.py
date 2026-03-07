import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QMessageBox, QInputDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from gen.main_ui import Ui_MainForm
from models.db_manager import (
    load_products, load_suppliers, delete_product, product_in_orders
)
from utils.helpers import get_image_path, calculate_discounted_price

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MainWindow(QWidget):
    def __init__(self, role, fio, login_window):
        super().__init__()
        self.role = role
        self.fio = fio
        self.login_window = login_window
        self.product_form = None
        self.orders_window = None

        self.ui = Ui_MainForm()
        self.ui.setupUi(self)

        self.setWindowTitle(f'Каталог товаров — {self._role_name()}')
        self.resize(1000, 700)

        logo_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                120, 36, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.ui.logo_label.setPixmap(pix)

        self.ui.fio_label.setText(self.fio)

        self._apply_role_visibility()

        self.ui.logout_btn.clicked.connect(self.logout)

        if self.role in ('manager', 'admin'):
            self.ui.sort_combo.addItems([
                'Без сортировки',
                'По количеству ↑',
                'По количеству ↓',
            ])
            self.ui.search_edit.textChanged.connect(self.apply_filters)
            self.ui.supplier_combo.currentIndexChanged.connect(
                self.apply_filters)
            self.ui.sort_combo.currentIndexChanged.connect(
                self.apply_filters)
            self.ui.orders_btn.clicked.connect(self.open_orders)

        if self.role == 'admin':
            self.ui.add_product_btn.clicked.connect(
                self.open_add_product)
            self.ui.delete_btn.clicked.connect(
                self.delete_selected_product)

        self.refresh_products()

    def _role_name(self):
        names = {
            'guest': 'Гость',
            'client': 'Клиент',
            'manager': 'Менеджер',
            'admin': 'Администратор',
        }
        return names.get(self.role, self.role)

    def _apply_role_visibility(self):
        show_filters = self.role in ('manager', 'admin')
        self.ui.search_edit.setVisible(show_filters)
        self.ui.supplier_combo.setVisible(show_filters)
        self.ui.sort_combo.setVisible(show_filters)

        self.ui.orders_btn.setVisible(
            self.role in ('manager', 'admin'))

        self.ui.add_product_btn.setVisible(self.role == 'admin')
        self.ui.delete_btn.setVisible(self.role == 'admin')

    def refresh_products(self):
        self.all_products = load_products()

        if self.role in ('manager', 'admin'):
            self._fill_supplier_combo()

        self.apply_filters()

    def _fill_supplier_combo(self):
        current_text = self.ui.supplier_combo.currentText()
        self.ui.supplier_combo.blockSignals(True)
        self.ui.supplier_combo.clear()
        self.ui.supplier_combo.addItem('Все поставщики')
        suppliers = load_suppliers()
        for s in suppliers:
            self.ui.supplier_combo.addItem(s['Name'])
        idx = self.ui.supplier_combo.findText(current_text)
        if idx >= 0:
            self.ui.supplier_combo.setCurrentIndex(idx)
        self.ui.supplier_combo.blockSignals(False)

    def apply_filters(self):
        result = list(self.all_products)

        if self.role in ('manager', 'admin'):
            text = self.ui.search_edit.text().strip().lower()
            if text:
                result = [
                    p for p in result
                    if text in p['Name'].lower()
                    or text in (p['Description'] or '').lower()
                    or text in p['ManufacturerName'].lower()
                    or text in p['SupplierName'].lower()
                    or text in p['CategoryName'].lower()
                ]

            supplier = self.ui.supplier_combo.currentText()
            if supplier and supplier != 'Все поставщики':
                result = [
                    p for p in result
                    if p['SupplierName'] == supplier
                ]

            sort_idx = self.ui.sort_combo.currentIndex()
            if sort_idx == 1:
                result.sort(key=lambda p: p['StockQuantity'])
            elif sort_idx == 2:
                result.sort(
                    key=lambda p: p['StockQuantity'], reverse=True)

        self._fill_cards(result)

    def _fill_cards(self, products):
        layout = self.ui.cards_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for product in products:
            card = self._create_product_card(product)
            layout.addWidget(card)

        layout.addStretch()
        self.ui.count_label.setText(f'Товаров: {len(products)}')

    def _create_product_card(self, product):
        card = QFrame()
        card.setObjectName('product_card')
        card.setFrameShape(QFrame.Shape.StyledPanel)

        bg_color = '#FFFFFF'
        if product['StockQuantity'] == 0:
            bg_color = '#ADD8E6'
        elif product['Discount'] > 15:
            bg_color = '#2E8B57'

        card.setStyleSheet(
            f'QFrame#product_card {{ background: {bg_color}; '
            f'border: 1px solid #E0E0E0; border-radius: 10px; }}')

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)

        header = QLabel(
            f'{product["CategoryName"]}  |  {product["Name"]}')
        header.setStyleSheet(
            'font-weight: bold; font-size: 15px; color: #2C3E50;')
        header.setWordWrap(True)
        card_layout.addWidget(header)

        desc = QLabel(product['Description'] or '')
        desc.setStyleSheet('color: #7F8C8D; font-size: 12px;')
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        mfr_label = QLabel(
            f'Производитель: {product["ManufacturerName"]}')
        mfr_label.setStyleSheet('font-size: 12px;')
        card_layout.addWidget(mfr_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        img_label = QLabel()
        img_label.setFixedSize(300, 200)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_path = get_image_path(product['ImagePath'])
        pix = QPixmap(img_path)
        if not pix.isNull():
            pix = pix.scaled(
                300, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pix)
        content_layout.addWidget(img_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        supplier_label = QLabel(
            f'Поставщик: {product["SupplierName"]}')
        supplier_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(supplier_label)

        price = product['Price']
        discount = product['Discount']
        if discount > 0:
            discounted = calculate_discounted_price(price, discount)
            price_label = QLabel()
            price_label.setTextFormat(Qt.TextFormat.RichText)
            price_label.setText(
                f'Цена: '
                f'<span style="text-decoration: line-through; '
                f'color: red;">{price:.2f}</span> '
                f'<span style="color: black; font-weight: bold;">'
                f'{discounted:.2f} руб.</span>')
            price_label.setStyleSheet('font-size: 13px;')
        else:
            price_label = QLabel(f'Цена: {price:.2f} руб.')
            price_label.setStyleSheet(
                'font-size: 13px; font-weight: bold;')
        info_layout.addWidget(price_label)

        unit_label = QLabel(f'Ед. изм.: {product["Unit"]}')
        unit_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(unit_label)

        stock_label = QLabel(
            f'На складе: {product["StockQuantity"]}')
        stock_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(stock_label)

        info_layout.addStretch()
        content_layout.addLayout(info_layout)

        if discount > 0:
            discount_label = QLabel(f'-{discount}%')
            discount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            discount_label.setFixedSize(60, 30)
            discount_label.setStyleSheet(
                'background: #E74C3C; color: white; '
                'border-radius: 6px; font-weight: bold; '
                'font-size: 14px;')
            content_layout.addWidget(
                discount_label,
                alignment=Qt.AlignmentFlag.AlignTop)

        content_layout.addStretch()
        card_layout.addLayout(content_layout)

        if self.role == 'admin':
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = (
                lambda event, p=product: self.open_edit_product(p))

        return card

    def open_add_product(self):
        if self.product_form is not None and self.product_form.isVisible():
            QMessageBox.information(
                self, 'Внимание',
                'Окно редактирования уже открыто.\n'
                'Закройте его перед открытием нового.')
            self.product_form.activateWindow()
            return
        from ui.product_form import ProductForm
        self.product_form = ProductForm(
            parent_window=self, product=None)
        self.product_form.show()

    def open_edit_product(self, product):
        if self.product_form is not None and self.product_form.isVisible():
            QMessageBox.information(
                self, 'Внимание',
                'Окно редактирования уже открыто.\n'
                'Закройте его перед открытием нового.')
            self.product_form.activateWindow()
            return
        from ui.product_form import ProductForm
        self.product_form = ProductForm(
            parent_window=self, product=product)
        self.product_form.show()

    def delete_selected_product(self):
        products = load_products()
        items = [f'{p["ProductID"]}: {p["Name"]}' for p in products]
        if not items:
            QMessageBox.information(
                self, 'Информация', 'Нет товаров для удаления.')
            return

        item, ok = QInputDialog.getItem(
            self, 'Удаление товара',
            'Выберите товар для удаления:', items, 0, False)
        if not ok:
            return

        product_id = int(item.split(':')[0])
        product_name = item.split(': ', 1)[1]

        if product_in_orders(product_id):
            QMessageBox.critical(
                self, 'Ошибка удаления',
                f'Невозможно удалить товар "{product_name}".\n'
                f'Он присутствует в заказе.')
            return

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f'Вы уверены, что хотите удалить товар\n'
            f'"{product_name}"?',
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            delete_product(product_id)
            self.refresh_products()
            QMessageBox.information(
                self, 'Успех',
                f'Товар "{product_name}" удалён.')

    def open_orders(self):
        from ui.orders_window import OrdersWindow
        self.orders_window = OrdersWindow(
            role=self.role, parent_window=self)
        self.orders_window.show()

    def logout(self):
        self.close()
        if self.login_window:
            self.login_window.on_logout()

    def closeEvent(self, event):
        if self.product_form and self.product_form.isVisible():
            self.product_form.close()
        if self.orders_window and self.orders_window.isVisible():
            self.orders_window.close()
        event.accept()
