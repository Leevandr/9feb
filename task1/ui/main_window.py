"""Главное окно — список товаров."""
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

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

        self.setWindowTitle(f'Каталог товаров — {self._role_name()}')
        self.resize(1000, 700)
        self._build_ui()
        self.refresh_products()

    def _role_name(self):
        names = {
            'guest': 'Гость',
            'client': 'Клиент',
            'manager': 'Менеджер',
            'admin': 'Администратор',
        }
        return names.get(self.role, self.role)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Верхняя панель
        top_panel = QHBoxLayout()

        logo_label = QLabel()
        logo_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                120, 36, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        top_panel.addWidget(logo_label)

        top_panel.addStretch()

        self.fio_label = QLabel(self.fio)
        self.fio_label.setStyleSheet(
            'font-weight: bold; font-size: 13px; color: #2C3E50;')
        top_panel.addWidget(self.fio_label)

        # Кнопка заказов (менеджер, админ)
        if self.role in ('manager', 'admin'):
            self.orders_btn = QPushButton('Заказы')
            self.orders_btn.clicked.connect(self.open_orders)
            top_panel.addWidget(self.orders_btn)

        # Кнопка добавления товара (админ)
        if self.role == 'admin':
            self.add_product_btn = QPushButton('Добавить товар')
            self.add_product_btn.setObjectName('add_btn')
            self.add_product_btn.clicked.connect(self.open_add_product)
            top_panel.addWidget(self.add_product_btn)

        logout_btn = QPushButton('Выход')
        logout_btn.clicked.connect(self.logout)
        top_panel.addWidget(logout_btn)

        main_layout.addLayout(top_panel)

        # Панель поиска/фильтрации/сортировки (менеджер, админ)
        if self.role in ('manager', 'admin'):
            filter_panel = QHBoxLayout()

            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText(
                'Поиск по названию, описанию, производителю...')
            self.search_edit.textChanged.connect(self.apply_filters)
            filter_panel.addWidget(self.search_edit, 2)

            self.supplier_combo = QComboBox()
            self.supplier_combo.currentIndexChanged.connect(
                self.apply_filters)
            filter_panel.addWidget(self.supplier_combo, 1)

            self.sort_combo = QComboBox()
            self.sort_combo.addItems([
                'Без сортировки',
                'По количеству ↑',
                'По количеству ↓',
            ])
            self.sort_combo.currentIndexChanged.connect(self.apply_filters)
            filter_panel.addWidget(self.sort_combo, 1)

            main_layout.addLayout(filter_panel)

        # Счётчик товаров
        self.count_label = QLabel()
        self.count_label.setStyleSheet('color: #7F8C8D; font-size: 12px;')
        main_layout.addWidget(self.count_label)

        # Кнопка удаления (админ)
        if self.role == 'admin':
            del_panel = QHBoxLayout()
            del_panel.addStretch()
            self.delete_btn = QPushButton('Удалить выбранный товар')
            self.delete_btn.setObjectName('delete_btn')
            self.delete_btn.setStyleSheet(
                'background: #E74C3C; color: white; '
                'border: none; border-radius: 6px; padding: 6px 14px;')
            self.delete_btn.clicked.connect(self.delete_selected_product)
            del_panel.addWidget(self.delete_btn)
            main_layout.addLayout(del_panel)

        # Область прокрутки с карточками
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('QScrollArea { border: none; }')

        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

    def refresh_products(self):
        """Перезагружает товары из БД и обновляет фильтры."""
        self.all_products = load_products()

        if self.role in ('manager', 'admin'):
            self._fill_supplier_combo()

        self.apply_filters()

    def _fill_supplier_combo(self):
        current_text = self.supplier_combo.currentText()
        self.supplier_combo.blockSignals(True)
        self.supplier_combo.clear()
        self.supplier_combo.addItem('Все поставщики')
        suppliers = load_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s['Name'])
        # Восстановить предыдущий выбор
        idx = self.supplier_combo.findText(current_text)
        if idx >= 0:
            self.supplier_combo.setCurrentIndex(idx)
        self.supplier_combo.blockSignals(False)

    def apply_filters(self):
        """Применяет поиск, фильтрацию и сортировку."""
        result = list(self.all_products)

        if self.role in ('manager', 'admin'):
            # Поиск
            text = self.search_edit.text().strip().lower()
            if text:
                result = [
                    p for p in result
                    if text in p['Name'].lower()
                    or text in (p['Description'] or '').lower()
                    or text in p['ManufacturerName'].lower()
                    or text in p['SupplierName'].lower()
                    or text in p['CategoryName'].lower()
                ]

            # Фильтр по поставщику
            supplier = self.supplier_combo.currentText()
            if supplier and supplier != 'Все поставщики':
                result = [
                    p for p in result
                    if p['SupplierName'] == supplier
                ]

            # Сортировка
            sort_idx = self.sort_combo.currentIndex()
            if sort_idx == 1:
                result.sort(key=lambda p: p['StockQuantity'])
            elif sort_idx == 2:
                result.sort(
                    key=lambda p: p['StockQuantity'], reverse=True)

        self._fill_cards(result)

    def _fill_cards(self, products):
        """Заполняет список карточками товаров."""
        # Очистка
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for product in products:
            card = self._create_product_card(product)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()
        self.count_label.setText(f'Товаров: {len(products)}')

    def _create_product_card(self, product):
        """Создаёт виджет-карточку товара по макету из ТЗ."""
        card = QFrame()
        card.setObjectName('product_card')
        card.setFrameShape(QFrame.Shape.StyledPanel)

        # Определяем цвет фона
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

        # Строка 1: Категория | Наименование
        header = QLabel(
            f'{product["CategoryName"]}  |  {product["Name"]}')
        header.setStyleSheet(
            'font-weight: bold; font-size: 15px; color: #2C3E50;')
        header.setWordWrap(True)
        card_layout.addWidget(header)

        # Строка 2: Описание
        desc = QLabel(product['Description'] or '')
        desc.setStyleSheet('color: #7F8C8D; font-size: 12px;')
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        # Строка 3: Производитель
        mfr_label = QLabel(
            f'Производитель: {product["ManufacturerName"]}')
        mfr_label.setStyleSheet('font-size: 12px;')
        card_layout.addWidget(mfr_label)

        # Строка 4: Фото + информация справа
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Фото
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

        # Информация справа от фото
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        supplier_label = QLabel(
            f'Поставщик: {product["SupplierName"]}')
        supplier_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(supplier_label)

        # Цена с учётом скидки
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

        unit_label = QLabel(
            f'Ед. изм.: {product["Unit"]}')
        unit_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(unit_label)

        stock_label = QLabel(
            f'На складе: {product["StockQuantity"]}')
        stock_label.setStyleSheet('font-size: 12px;')
        info_layout.addWidget(stock_label)

        info_layout.addStretch()
        content_layout.addLayout(info_layout)

        # Скидка (бейдж справа)
        if discount > 0:
            discount_label = QLabel(f'-{discount}%')
            discount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            discount_label.setFixedSize(60, 30)
            discount_label.setStyleSheet(
                'background: #E74C3C; color: white; '
                'border-radius: 6px; font-weight: bold; font-size: 14px;')
            content_layout.addWidget(
                discount_label,
                alignment=Qt.AlignmentFlag.AlignTop)

        content_layout.addStretch()
        card_layout.addLayout(content_layout)

        # Для администратора — клик по карточке = редактирование
        if self.role == 'admin':
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = (
                lambda event, p=product: self.open_edit_product(p))
            card.setProperty('product_id', product['ProductID'])

        return card

    # ---- Действия ----

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
        """Удаление товара — нужно выбрать карточку."""
        # Находим карточку, на которую последний раз кликнули
        # Используем фокус
        focused = self.scroll_widget.focusWidget()

        # Альтернативный подход: показать диалог выбора
        from PyQt6.QtWidgets import QInputDialog
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

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
