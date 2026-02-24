import sys
import os
import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QFont, QCursor
from PyQt6.QtCore import Qt

from gen.main_ui import Ui_MainForm
from gen.auth_ui import Ui_AuthForm
from gen.buyer_ui import Ui_BuyerForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pharmacy.db')

# ============================================================
#  Глобальные стили приложения
# ============================================================
APP_STYLE = """
QWidget {
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
}
#top_panel, #filter_panel {
    background: #FFFFFF;
    border-bottom: 1px solid #E8E8E8;
}
#bottom_panel {
    background: #FFFFFF;
    border-top: 1px solid #E8E8E8;
}
QScrollArea {
    background: #F0F2F5;
}
QScrollArea > QWidget > QWidget {
    background: #F0F2F5;
}
QLineEdit {
    padding: 6px 10px;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    background: white;
}
QLineEdit:focus {
    border: 2px solid #3498DB;
}
QComboBox {
    padding: 6px 10px;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    background: white;
}
QSpinBox {
    padding: 6px 8px;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    background: white;
}
QPushButton {
    padding: 6px 14px;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    background: white;
    color: #2C3E50;
}
QPushButton:hover {
    background: #F8F9FA;
    border-color: #BDC3C7;
}
#search_btn {
    background: #3498DB;
    color: white;
    border: none;
    font-weight: bold;
}
#search_btn:hover {
    background: #2E86C1;
}
#cart_btn {
    background: #E8F8F5;
    color: #1ABC9C;
    border: 1px solid #A3E4D7;
    font-weight: bold;
}
#cart_btn:hover {
    background: #D1F2EB;
}
#auth_btn {
    background: #EBF5FB;
    color: #2E86C1;
    border: 1px solid #AED6F1;
    font-weight: bold;
}
#auth_btn:hover {
    background: #D4E6F1;
}
#checkout_btn {
    background: #27AE60;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: bold;
}
#checkout_btn:hover {
    background: #2ECC71;
}
QTabWidget::pane {
    border: none;
}
QTabBar::tab {
    padding: 10px 20px;
    font-size: 13px;
}
QTabBar::tab:selected {
    color: #2E86C1;
    font-weight: bold;
    border-bottom: 2px solid #2E86C1;
}
QTableWidget {
    border: 1px solid #E8E8E8;
    border-radius: 8px;
    gridline-color: #F0F0F0;
    alternate-background-color: #FAFBFC;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background: #F8F9FA;
    border: none;
    border-bottom: 1px solid #E8E8E8;
    padding: 8px;
    font-weight: bold;
    color: #566573;
}
"""

CARD_STYLE = """
QFrame#product_card {
    background: white;
    border: 1px solid #E5E8EB;
    border-radius: 14px;
}
QFrame#product_card:hover {
    border: 2px solid #27AE60;
}
"""

CARD_BTN_STYLE = """
QPushButton {
    background: #27AE60;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover {
    background: #2ECC71;
}
QPushButton:pressed {
    background: #229954;
}
"""


# ============================================================
#  Вспомогательные функции работы с БД
# ============================================================
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_products():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unique_values(column):
    conn = get_connection()
    rows = conn.execute(
        f'SELECT DISTINCT {column} FROM products ORDER BY {column}'
    ).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


# ============================================================
#  Общая корзина
# ============================================================
shared_cart = []


# ============================================================
#  Создание карточки товара (общее для всех окон)
# ============================================================
def create_product_card(product, on_add_to_cart):
    """Создаёт виджет-карточку для одного препарата."""
    card = QFrame()
    card.setObjectName("product_card")
    card.setStyleSheet(CARD_STYLE)
    card.setFixedWidth(290)
    card.setMinimumHeight(370)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(6)

    # Фото
    img_label = QLabel()
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    photo_path = os.path.join(BASE_DIR, product['photo']) \
        if product['photo'] else ''
    if photo_path and os.path.exists(photo_path):
        pix = QPixmap(photo_path).scaled(
            140, 140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pix)
    img_label.setFixedHeight(145)
    layout.addWidget(img_label)

    # Название
    name_lbl = QLabel(product['name'])
    name_lbl.setStyleSheet(
        'font-weight: bold; font-size: 15px; color: #2C3E50;')
    name_lbl.setWordWrap(True)
    layout.addWidget(name_lbl)

    # Форма выпуска
    form_lbl = QLabel(product['release_form'])
    form_lbl.setStyleSheet('color: #7F8C8D; font-size: 12px;')
    layout.addWidget(form_lbl)

    # Группа заболеваний
    group_lbl = QLabel(product['disease_group'])
    group_lbl.setStyleSheet('color: #ABB2B9; font-size: 11px;')
    layout.addWidget(group_lbl)

    # Рецептурность (бейдж)
    rx = product['prescription']
    if rx == 'Рецептурный':
        rx_lbl = QLabel('Rx  По рецепту')
        rx_lbl.setStyleSheet(
            'color: #E74C3C; font-size: 11px; font-weight: bold;')
    else:
        rx_lbl = QLabel('Без рецепта')
        rx_lbl.setStyleSheet(
            'color: #27AE60; font-size: 11px;')
    layout.addWidget(rx_lbl)

    # Разделитель
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet('background: #ECF0F1; max-height: 1px;')
    layout.addWidget(line)

    # Цена + кнопка
    bottom = QHBoxLayout()
    price_lbl = QLabel(f'{product["price"]:.0f} руб')
    price_lbl.setStyleSheet(
        'font-weight: bold; font-size: 17px; color: #27AE60;')
    bottom.addWidget(price_lbl)

    bottom.addStretch()

    btn = QPushButton('В корзину')
    btn.setStyleSheet(CARD_BTN_STYLE)
    btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    btn.setFixedHeight(34)
    btn.clicked.connect(
        lambda checked, p=product: on_add_to_cart(p))
    bottom.addWidget(btn)

    layout.addLayout(bottom)
    layout.addStretch()

    return card


def fill_grid(grid_layout, data, on_add_to_cart, count_label=None):
    """Очищает grid и заполняет карточками."""
    while grid_layout.count():
        child = grid_layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    cols = 3
    for i, product in enumerate(data):
        card = create_product_card(product, on_add_to_cart)
        grid_layout.addWidget(card, i // cols, i % cols)

    # Выравнивание по верху
    grid_layout.setRowStretch(len(data) // cols + 1, 1)

    if count_label:
        count_label.setText(f'Препаратов: {len(data)}')


# ============================================================
#  ГЛАВНОЕ ОКНО (гость)
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)

        self.products = load_products()
        self.fill_filters()
        self._fill(self.products)

        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset)
        self.ui.auth_btn.clicked.connect(self.open_auth)
        self.ui.cart_btn.clicked.connect(self.show_cart_dialog)

    def fill_filters(self):
        self.ui.disease_combo.clear()
        self.ui.disease_combo.addItem('Все группы')
        self.ui.disease_combo.addItems(
            get_unique_values('disease_group'))

        self.ui.form_combo.clear()
        self.ui.form_combo.addItem('Все формы')
        self.ui.form_combo.addItems(
            get_unique_values('release_form'))

        self.ui.manufacturer_combo.clear()
        self.ui.manufacturer_combo.addItem('Все производители')
        self.ui.manufacturer_combo.addItem('Отечественный')
        self.ui.manufacturer_combo.addItem('Импортный')

        self.ui.prescription_combo.clear()
        self.ui.prescription_combo.addItem('Все')
        self.ui.prescription_combo.addItem('Рецептурный')
        self.ui.prescription_combo.addItem('Безрецептурный')

    def _fill(self, data):
        fill_grid(
            self.ui.cards_grid, data,
            self._add_to_cart, self.ui.count_label)

    def _add_to_cart(self, product):
        pid = product['id']
        name = product['name']
        price = product['price']
        for item in shared_cart:
            if item['product_id'] == pid:
                item['quantity'] += 1
                self._update_cart_btn()
                QMessageBox.information(
                    self, 'Корзина',
                    f'{name} — кол-во: {item["quantity"]}')
                return
        shared_cart.append({
            'product_id': pid, 'name': name,
            'price': price, 'quantity': 1
        })
        self._update_cart_btn()
        QMessageBox.information(
            self, 'Корзина', f'{name} добавлен в корзину')

    def _update_cart_btn(self):
        total_qty = sum(i['quantity'] for i in shared_cart)
        self.ui.cart_btn.setText(f'Корзина ({total_qty})')

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        disease = self.ui.disease_combo.currentText()
        form = self.ui.form_combo.currentText()
        mfr = self.ui.manufacturer_combo.currentText()
        rx = self.ui.prescription_combo.currentText()
        p_min = self.ui.price_min.value()
        p_max = self.ui.price_max.value()

        result = self.products
        if text:
            result = [p for p in result
                      if text in p['name'].lower()
                      or text in p['active_ingredient'].lower()]
        if disease != 'Все группы':
            result = [p for p in result
                      if p['disease_group'] == disease]
        if form != 'Все формы':
            result = [p for p in result
                      if p['release_form'] == form]
        if mfr != 'Все производители':
            result = [p for p in result
                      if mfr.lower() in p['manufacturer'].lower()]
        if rx != 'Все':
            result = [p for p in result
                      if p['prescription'] == rx]
        if p_max > 0:
            result = [p for p in result
                      if p_min <= p['price'] <= p_max]
        self._fill(result)

    def reset(self):
        self.ui.search_edit.clear()
        self.ui.disease_combo.setCurrentIndex(0)
        self.ui.form_combo.setCurrentIndex(0)
        self.ui.manufacturer_combo.setCurrentIndex(0)
        self.ui.prescription_combo.setCurrentIndex(0)
        self.ui.price_min.setValue(0)
        self.ui.price_max.setValue(0)
        self._fill(self.products)

    def show_cart_dialog(self):
        if not shared_cart:
            QMessageBox.information(self, 'Корзина', 'Корзина пуста')
            return
        dlg = QDialog(self)
        dlg.setWindowTitle('Корзина')
        dlg.resize(500, 350)
        lay = QVBoxLayout(dlg)
        tbl = QTableWidget()
        tbl.setRowCount(len(shared_cart))
        tbl.setColumnCount(3)
        tbl.setHorizontalHeaderLabels(
            ['Наименование', 'Кол-во', 'Сумма'])
        total = 0
        for i, item in enumerate(shared_cart):
            tbl.setItem(i, 0, QTableWidgetItem(item['name']))
            tbl.setItem(i, 1, QTableWidgetItem(
                str(item['quantity'])))
            s = item['price'] * item['quantity']
            tbl.setItem(i, 2, QTableWidgetItem(f'{s:.0f} руб'))
            total += s
        tbl.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(tbl)
        lay.addWidget(QLabel(f'Итого: {total:.0f} руб'))
        lay.addWidget(QLabel('Для оформления заказа авторизуйтесь'))
        dlg.exec()

    def open_auth(self):
        self.auth_win = AuthWindow(parent_main=self)
        self.auth_win.show()


# ============================================================
#  АВТОРИЗАЦИЯ / РЕГИСТРАЦИЯ
# ============================================================
class AuthWindow(QWidget):
    def __init__(self, parent_main=None):
        super().__init__()
        self.ui = Ui_AuthForm()
        self.ui.setupUi(self)
        self.parent_main = parent_main

        self.ui.login_btn.clicked.connect(self.do_login)
        self.ui.register_btn.clicked.connect(self.do_register)

    def do_login(self):
        email = self.ui.login_email_edit.text().strip()
        password = self.ui.login_password_edit.text().strip()
        if not email or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        conn = get_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        ).fetchone()
        conn.close()
        if user is None:
            QMessageBox.warning(
                self, 'Ошибка', 'Неверный e-mail или пароль')
            return
        self.open_buyer(dict(user))

    def do_register(self):
        fio = self.ui.reg_fio_edit.text().strip()
        email = self.ui.reg_email_edit.text().strip()
        phone = self.ui.reg_phone_edit.text().strip()
        pwd = self.ui.reg_password_edit.text().strip()
        pwd2 = self.ui.reg_password2_edit.text().strip()
        if not fio or not email or not pwd:
            QMessageBox.warning(
                self, 'Ошибка', 'Заполните ФИО, e-mail и пароль')
            return
        if pwd != pwd2:
            QMessageBox.warning(
                self, 'Ошибка', 'Пароли не совпадают')
            return
        conn = get_connection()
        existing = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()
        if existing:
            conn.close()
            QMessageBox.warning(
                self, 'Ошибка',
                'Пользователь с таким e-mail уже существует')
            return
        conn.execute(
            'INSERT INTO users (fio, email, phone, password) '
            'VALUES (?,?,?,?)',
            (fio, email, phone, pwd))
        conn.commit()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()
        QMessageBox.information(
            self, 'Успех',
            'Регистрация прошла успешно! Вы вошли в систему.')
        self.open_buyer(dict(user))

    def open_buyer(self, user_dict):
        self.buyer_win = BuyerWindow(user_dict)
        self.buyer_win.show()
        self.close()
        if self.parent_main:
            self.parent_main.close()


# ============================================================
#  ОКНО ПОКУПАТЕЛЯ
# ============================================================
class BuyerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_BuyerForm()
        self.ui.setupUi(self)
        self.user = user
        self.products = load_products()
        self.cart = shared_cart

        # --- Каталог ---
        self.fill_filters()
        self._fill_catalog(self.products)
        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset_search)

        # --- Корзина ---
        self.ui.plus_btn.clicked.connect(self.cart_plus)
        self.ui.minus_btn.clicked.connect(self.cart_minus)
        self.ui.remove_btn.clicked.connect(self.cart_remove)
        self.ui.checkout_btn.clicked.connect(self.checkout)
        self.refresh_cart()

        # --- Профиль ---
        self.ui.profile_fio.setText(f'ФИО: {self.user["fio"]}')
        self.ui.profile_email.setText(
            f'E-mail: {self.user["email"]}')
        self.ui.profile_phone.setText(
            f'Телефон: {self.user["phone"]}')
        self.ui.add_address_btn.clicked.connect(self.add_address)
        self.refresh_addresses()
        self.refresh_orders()

    # -------------------- Каталог --------------------
    def fill_filters(self):
        self.ui.disease_combo.clear()
        self.ui.disease_combo.addItem('Все группы')
        self.ui.disease_combo.addItems(
            get_unique_values('disease_group'))

        self.ui.form_combo.clear()
        self.ui.form_combo.addItem('Все формы')
        self.ui.form_combo.addItems(
            get_unique_values('release_form'))

        self.ui.manufacturer_combo.clear()
        self.ui.manufacturer_combo.addItem('Все производители')
        self.ui.manufacturer_combo.addItem('Отечественный')
        self.ui.manufacturer_combo.addItem('Импортный')

        self.ui.prescription_combo.clear()
        self.ui.prescription_combo.addItem('Все')
        self.ui.prescription_combo.addItem('Рецептурный')
        self.ui.prescription_combo.addItem('Безрецептурный')

    def _fill_catalog(self, data):
        fill_grid(
            self.ui.cards_grid, data,
            self._add_to_cart)

    def _add_to_cart(self, product):
        pid = product['id']
        name = product['name']
        price = product['price']
        for item in self.cart:
            if item['product_id'] == pid:
                item['quantity'] += 1
                self.refresh_cart()
                QMessageBox.information(
                    self, 'Корзина',
                    f'{name} — кол-во: {item["quantity"]}')
                return
        self.cart.append({
            'product_id': pid, 'name': name,
            'price': price, 'quantity': 1
        })
        self.refresh_cart()
        QMessageBox.information(
            self, 'Корзина', f'{name} добавлен в корзину')

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        disease = self.ui.disease_combo.currentText()
        form = self.ui.form_combo.currentText()
        mfr = self.ui.manufacturer_combo.currentText()
        rx = self.ui.prescription_combo.currentText()
        p_min = self.ui.price_min.value()
        p_max = self.ui.price_max.value()

        result = self.products
        if text:
            result = [p for p in result
                      if text in p['name'].lower()
                      or text in p['active_ingredient'].lower()]
        if disease != 'Все группы':
            result = [p for p in result
                      if p['disease_group'] == disease]
        if form != 'Все формы':
            result = [p for p in result
                      if p['release_form'] == form]
        if mfr != 'Все производители':
            result = [p for p in result
                      if mfr.lower() in p['manufacturer'].lower()]
        if rx != 'Все':
            result = [p for p in result
                      if p['prescription'] == rx]
        if p_max > 0:
            result = [p for p in result
                      if p_min <= p['price'] <= p_max]
        self._fill_catalog(result)

    def reset_search(self):
        self.ui.search_edit.clear()
        self.ui.disease_combo.setCurrentIndex(0)
        self.ui.form_combo.setCurrentIndex(0)
        self.ui.manufacturer_combo.setCurrentIndex(0)
        self.ui.prescription_combo.setCurrentIndex(0)
        self.ui.price_min.setValue(0)
        self.ui.price_max.setValue(0)
        self._fill_catalog(self.products)

    # -------------------- Корзина --------------------
    def refresh_cart(self):
        self.ui.cart_table.setRowCount(len(self.cart))
        self.ui.cart_table.setColumnCount(4)
        self.ui.cart_table.setHorizontalHeaderLabels(
            ['Наименование', 'Цена', 'Кол-во', 'Сумма'])
        self.ui.cart_table.horizontalHeader() \
            .setStretchLastSection(True)
        self.ui.cart_table.setAlternatingRowColors(True)
        total = 0
        for i, item in enumerate(self.cart):
            self.ui.cart_table.setItem(
                i, 0, QTableWidgetItem(item['name']))
            self.ui.cart_table.setItem(
                i, 1, QTableWidgetItem(
                    f'{item["price"]:.0f} руб'))
            self.ui.cart_table.setItem(
                i, 2, QTableWidgetItem(str(item['quantity'])))
            s = item['price'] * item['quantity']
            self.ui.cart_table.setItem(
                i, 3, QTableWidgetItem(f'{s:.0f} руб'))
            total += s
        self.ui.cart_total_label.setText(
            f'Итого: {total:.0f} руб')

    def cart_plus(self):
        row = self.ui.cart_table.currentRow()
        if row >= 0:
            self.cart[row]['quantity'] += 1
            self.refresh_cart()

    def cart_minus(self):
        row = self.ui.cart_table.currentRow()
        if row >= 0:
            if self.cart[row]['quantity'] > 1:
                self.cart[row]['quantity'] -= 1
            else:
                self.cart.pop(row)
            self.refresh_cart()

    def cart_remove(self):
        row = self.ui.cart_table.currentRow()
        if row >= 0:
            self.cart.pop(row)
            self.refresh_cart()

    # -------------------- Оформление заказа --------------------
    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, 'Внимание', 'Корзина пуста')
            return

        dlg = QDialog(self)
        dlg.setWindowTitle('Оформление заказа')
        dlg.resize(550, 500)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel('Состав заказа:'))
        order_tbl = QTableWidget()
        order_tbl.setRowCount(len(self.cart))
        order_tbl.setColumnCount(4)
        order_tbl.setHorizontalHeaderLabels(
            ['Наименование', 'Цена', 'Кол-во', 'Сумма'])
        order_tbl.horizontalHeader().setStretchLastSection(True)
        total = 0
        for i, item in enumerate(self.cart):
            order_tbl.setItem(
                i, 0, QTableWidgetItem(item['name']))
            order_tbl.setItem(
                i, 1, QTableWidgetItem(
                    f'{item["price"]:.0f} руб'))
            order_tbl.setItem(
                i, 2, QTableWidgetItem(str(item['quantity'])))
            s = item['price'] * item['quantity']
            order_tbl.setItem(
                i, 3, QTableWidgetItem(f'{s:.0f} руб'))
            total += s
        layout.addWidget(order_tbl)

        total_label = QLabel(f'Сумма заказа: {total:.0f} руб')
        total_label.setStyleSheet(
            'font-weight: bold; font-size: 14px; color: #27AE60;')
        layout.addWidget(total_label)

        layout.addWidget(QLabel(
            f'Покупатель: {self.user["fio"]} | '
            f'{self.user["email"]} | {self.user["phone"]}'))

        pay_layout = QHBoxLayout()
        pay_layout.addWidget(QLabel('Способ оплаты:'))
        pay_combo = QComboBox()
        pay_combo.addItems(['Наличные', 'Банковская карта'])
        pay_layout.addWidget(pay_combo)
        layout.addLayout(pay_layout)

        addr_layout = QHBoxLayout()
        addr_layout.addWidget(QLabel('Адрес доставки:'))
        addr_combo = QComboBox()
        conn = get_connection()
        addrs = conn.execute(
            'SELECT address FROM addresses WHERE user_id = ?',
            (self.user['id'],)).fetchall()
        conn.close()
        for a in addrs:
            addr_combo.addItem(a['address'])
        addr_combo.addItem('-- Новый адрес --')
        addr_layout.addWidget(addr_combo)
        layout.addLayout(addr_layout)

        new_addr_edit = QLineEdit()
        new_addr_edit.setPlaceholderText(
            'Введите новый адрес доставки')
        new_addr_edit.setVisible(False)
        layout.addWidget(new_addr_edit)

        def on_addr_changed(idx):
            new_addr_edit.setVisible(
                addr_combo.currentText() == '-- Новый адрес --')

        addr_combo.currentIndexChanged.connect(on_addr_changed)

        confirm_btn = QPushButton('Подтвердить заказ')
        confirm_btn.setObjectName('checkout_btn')
        confirm_btn.setMinimumHeight(40)
        layout.addWidget(confirm_btn)

        def confirm_order():
            address = addr_combo.currentText()
            if address == '-- Новый адрес --':
                address = new_addr_edit.text().strip()
                if not address:
                    QMessageBox.warning(
                        dlg, 'Ошибка', 'Введите адрес доставки')
                    return
                conn = get_connection()
                conn.execute(
                    'INSERT INTO addresses (user_id, address) '
                    'VALUES (?,?)',
                    (self.user['id'], address))
                conn.commit()
                conn.close()

            payment = pay_combo.currentText()
            order_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            delivery_date = (
                datetime.now() + timedelta(days=5)
            ).strftime('%Y-%m-%d')

            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO orders
                    (user_id, payment_method, delivery_address,
                     total, status, order_date, delivery_date)
                VALUES (?,?,?,?,?,?,?)
            ''', (self.user['id'], payment, address,
                  total, 'Новый', order_date, delivery_date))
            order_id = cur.lastrowid

            for item in self.cart:
                cur.execute('''
                    INSERT INTO order_items
                        (order_id, product_id, quantity, price)
                    VALUES (?,?,?,?)
                ''', (order_id, item['product_id'],
                      item['quantity'], item['price']))

            conn.commit()
            conn.close()

            self.cart.clear()
            self.refresh_cart()
            self.refresh_orders()
            self.refresh_addresses()
            dlg.accept()

            QMessageBox.information(
                self, 'Заказ оформлен',
                f'Номер заказа: #{order_id}\n'
                f'Сумма: {total:.0f} руб\n'
                f'Оплата: {payment}\n'
                f'Адрес: {address}\n'
                f'Примерная дата доставки: {delivery_date}')

        confirm_btn.clicked.connect(confirm_order)
        dlg.exec()

    # -------------------- Заказы --------------------
    def refresh_orders(self):
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM orders WHERE user_id = ? '
            'ORDER BY id DESC',
            (self.user['id'],)).fetchall()
        conn.close()

        self.ui.orders_table.setRowCount(len(rows))
        self.ui.orders_table.setColumnCount(6)
        self.ui.orders_table.setHorizontalHeaderLabels(
            ['#', 'Дата', 'Сумма', 'Оплата',
             'Статус', 'Дата доставки'])
        self.ui.orders_table.horizontalHeader() \
            .setStretchLastSection(True)
        self.ui.orders_table.setAlternatingRowColors(True)
        for i, o in enumerate(rows):
            self.ui.orders_table.setItem(
                i, 0, QTableWidgetItem(str(o['id'])))
            self.ui.orders_table.setItem(
                i, 1, QTableWidgetItem(o['order_date']))
            self.ui.orders_table.setItem(
                i, 2, QTableWidgetItem(
                    f'{o["total"]:.0f} руб'))
            self.ui.orders_table.setItem(
                i, 3, QTableWidgetItem(o['payment_method']))
            self.ui.orders_table.setItem(
                i, 4, QTableWidgetItem(o['status']))
            self.ui.orders_table.setItem(
                i, 5, QTableWidgetItem(o['delivery_date']))

        self.ui.profile_orders_count.setText(
            f'Заказов: {len(rows)}')

    # -------------------- Адреса --------------------
    def refresh_addresses(self):
        conn = get_connection()
        addrs = conn.execute(
            'SELECT * FROM addresses WHERE user_id = ?',
            (self.user['id'],)).fetchall()
        conn.close()
        self.ui.addresses_list.clear()
        for a in addrs:
            self.ui.addresses_list.addItem(a['address'])

    def add_address(self):
        address = self.ui.new_address_edit.text().strip()
        if not address:
            QMessageBox.warning(self, 'Ошибка', 'Введите адрес')
            return
        conn = get_connection()
        conn.execute(
            'INSERT INTO addresses (user_id, address) '
            'VALUES (?,?)',
            (self.user['id'], address))
        conn.commit()
        conn.close()
        self.ui.new_address_edit.clear()
        self.refresh_addresses()
        QMessageBox.information(self, 'Успех', 'Адрес добавлен')


# ============================================================
#  ЗАПУСК
# ============================================================
if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from create_data import create_database
        create_database()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
