import sys
import os
import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from gen.main_ui import Ui_MainForm
from gen.auth_ui import Ui_AuthForm
from gen.buyer_ui import Ui_BuyerForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pharmacy.db')


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


def make_photo_label(photo_path, size=50):
    """Создаёт QLabel с изображением для вставки в таблицу."""
    lbl = QLabel()
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    full = os.path.join(BASE_DIR, photo_path) if photo_path else ''
    if full and os.path.exists(full):
        pix = QPixmap(full).scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        lbl.setPixmap(pix)
    return lbl


# ============================================================
#  Общая корзина (in-memory, передаётся между окнами)
#  Формат: [{product_id, name, price, quantity}, ...]
# ============================================================
shared_cart = []


# ============================================================
#  ГЛАВНОЕ ОКНО (гость — каталог + корзина + авторизация)
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)

        self.products = load_products()
        self.fill_filters()
        self.fill_table(self.products)

        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset)
        self.ui.auth_btn.clicked.connect(self.open_auth)
        self.ui.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.ui.cart_btn.clicked.connect(self.show_cart_dialog)

    def fill_filters(self):
        groups = get_unique_values('disease_group')
        self.ui.disease_combo.clear()
        self.ui.disease_combo.addItem('Все группы')
        self.ui.disease_combo.addItems(groups)

        forms = get_unique_values('release_form')
        self.ui.form_combo.clear()
        self.ui.form_combo.addItem('Все формы')
        self.ui.form_combo.addItems(forms)

        self.ui.manufacturer_combo.clear()
        self.ui.manufacturer_combo.addItem('Все производители')
        self.ui.manufacturer_combo.addItem('Отечественный')
        self.ui.manufacturer_combo.addItem('Импортный')

        self.ui.prescription_combo.clear()
        self.ui.prescription_combo.addItem('Все')
        self.ui.prescription_combo.addItem('Рецептурный')
        self.ui.prescription_combo.addItem('Безрецептурный')

    def fill_table(self, data):
        self.ui.table.setRowCount(len(data))
        self.ui.table.setColumnCount(7)
        self.ui.table.setHorizontalHeaderLabels(
            ['Фото', 'Название', 'Инструкция', 'Форма выпуска',
             'Цена', 'Группа', 'Рецепт'])
        self.ui.table.setColumnWidth(0, 60)
        self.ui.table.setColumnWidth(1, 150)
        self.ui.table.setColumnWidth(2, 280)
        self.ui.table.setColumnWidth(3, 120)
        self.ui.table.setColumnWidth(4, 80)
        self.ui.table.setColumnWidth(5, 160)
        self.ui.table.setColumnWidth(6, 130)

        for i, p in enumerate(data):
            self.ui.table.setRowHeight(i, 58)
            self.ui.table.setCellWidget(
                i, 0, make_photo_label(p['photo']))
            self.ui.table.setItem(
                i, 1, QTableWidgetItem(p['name']))
            self.ui.table.setItem(
                i, 2, QTableWidgetItem(p['instruction']))
            self.ui.table.setItem(
                i, 3, QTableWidgetItem(p['release_form']))
            self.ui.table.setItem(
                i, 4, QTableWidgetItem(str(p['price'])))
            self.ui.table.setItem(
                i, 5, QTableWidgetItem(p['disease_group']))
            self.ui.table.setItem(
                i, 6, QTableWidgetItem(p['prescription']))

        self.ui.count_label.setText(f'Препаратов: {len(data)}')

    # ---------- Поиск / фильтрация ----------
    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        disease = self.ui.disease_combo.currentText()
        form = self.ui.form_combo.currentText()
        mfr = self.ui.manufacturer_combo.currentText()
        prescription = self.ui.prescription_combo.currentText()
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
        if prescription != 'Все':
            result = [p for p in result
                      if p['prescription'] == prescription]
        if p_max > 0:
            result = [p for p in result
                      if p_min <= p['price'] <= p_max]
        self.fill_table(result)

    def reset(self):
        self.ui.search_edit.clear()
        self.ui.disease_combo.setCurrentIndex(0)
        self.ui.form_combo.setCurrentIndex(0)
        self.ui.manufacturer_combo.setCurrentIndex(0)
        self.ui.prescription_combo.setCurrentIndex(0)
        self.ui.price_min.setValue(0)
        self.ui.price_max.setValue(0)
        self.fill_table(self.products)

    # ---------- Корзина (гостевая) ----------
    def add_to_cart(self):
        row = self.ui.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите препарат')
            return
        name = self.ui.table.item(row, 1).text()
        price = float(self.ui.table.item(row, 4).text())
        pid = None
        for p in self.products:
            if p['name'] == name and p['price'] == price:
                pid = p['id']
                break
        for item in shared_cart:
            if item['product_id'] == pid:
                item['quantity'] += 1
                self.update_cart_btn()
                QMessageBox.information(
                    self, 'Корзина',
                    f'{name} — кол-во увеличено до {item["quantity"]}')
                return
        shared_cart.append({
            'product_id': pid, 'name': name,
            'price': price, 'quantity': 1
        })
        self.update_cart_btn()
        QMessageBox.information(
            self, 'Корзина', f'{name} добавлен в корзину')

    def update_cart_btn(self):
        total_qty = sum(i['quantity'] for i in shared_cart)
        self.ui.cart_btn.setText(f'Корзина ({total_qty})')

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
        tbl.setHorizontalHeaderLabels(['Наименование', 'Кол-во', 'Сумма'])
        total = 0
        for i, item in enumerate(shared_cart):
            tbl.setItem(i, 0, QTableWidgetItem(item['name']))
            tbl.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            s = item['price'] * item['quantity']
            tbl.setItem(i, 2, QTableWidgetItem(f'{s} руб'))
            total += s
        lay.addWidget(tbl)
        lay.addWidget(QLabel(f'Итого: {total} руб'))
        info = QLabel('Для оформления заказа авторизуйтесь')
        lay.addWidget(info)
        dlg.exec()

    # ---------- Авторизация ----------
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
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают')
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
            (fio, email, phone, pwd)
        )
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
#  ОКНО ПОКУПАТЕЛЯ (каталог, корзина, оформление, заказы, профиль)
# ============================================================
class BuyerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_BuyerForm()
        self.ui.setupUi(self)
        self.user = user  # dict: id, fio, email, phone, password
        self.products = load_products()
        self.cart = shared_cart

        # --- Каталог ---
        self.fill_filters()
        self.fill_catalog(self.products)
        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset_search)
        self.ui.add_to_cart_btn.clicked.connect(self.add_to_cart)

        # --- Корзина ---
        self.ui.plus_btn.clicked.connect(self.cart_plus)
        self.ui.minus_btn.clicked.connect(self.cart_minus)
        self.ui.remove_btn.clicked.connect(self.cart_remove)
        self.ui.checkout_btn.clicked.connect(self.checkout)
        self.refresh_cart()

        # --- Профиль ---
        self.ui.profile_fio.setText(f'ФИО: {self.user["fio"]}')
        self.ui.profile_email.setText(f'E-mail: {self.user["email"]}')
        self.ui.profile_phone.setText(f'Телефон: {self.user["phone"]}')
        self.ui.add_address_btn.clicked.connect(self.add_address)
        self.refresh_addresses()
        self.refresh_orders()

    # -------------------- Каталог --------------------
    def fill_filters(self):
        groups = get_unique_values('disease_group')
        self.ui.disease_combo.clear()
        self.ui.disease_combo.addItem('Все группы')
        self.ui.disease_combo.addItems(groups)

        forms = get_unique_values('release_form')
        self.ui.form_combo.clear()
        self.ui.form_combo.addItem('Все формы')
        self.ui.form_combo.addItems(forms)

        self.ui.manufacturer_combo.clear()
        self.ui.manufacturer_combo.addItem('Все производители')
        self.ui.manufacturer_combo.addItem('Отечественный')
        self.ui.manufacturer_combo.addItem('Импортный')

        self.ui.prescription_combo.clear()
        self.ui.prescription_combo.addItem('Все')
        self.ui.prescription_combo.addItem('Рецептурный')
        self.ui.prescription_combo.addItem('Безрецептурный')

    def fill_catalog(self, data):
        self.ui.catalog_table.setRowCount(len(data))
        self.ui.catalog_table.setColumnCount(7)
        self.ui.catalog_table.setHorizontalHeaderLabels(
            ['Фото', 'Название', 'Инструкция', 'Форма выпуска',
             'Цена', 'Группа', 'Рецепт'])
        self.ui.catalog_table.setColumnWidth(0, 60)
        self.ui.catalog_table.setColumnWidth(1, 150)
        self.ui.catalog_table.setColumnWidth(2, 280)
        self.ui.catalog_table.setColumnWidth(3, 120)
        self.ui.catalog_table.setColumnWidth(4, 80)
        self.ui.catalog_table.setColumnWidth(5, 160)
        self.ui.catalog_table.setColumnWidth(6, 130)

        for i, p in enumerate(data):
            self.ui.catalog_table.setRowHeight(i, 58)
            self.ui.catalog_table.setCellWidget(
                i, 0, make_photo_label(p['photo']))
            self.ui.catalog_table.setItem(
                i, 1, QTableWidgetItem(p['name']))
            self.ui.catalog_table.setItem(
                i, 2, QTableWidgetItem(p['instruction']))
            self.ui.catalog_table.setItem(
                i, 3, QTableWidgetItem(p['release_form']))
            self.ui.catalog_table.setItem(
                i, 4, QTableWidgetItem(str(p['price'])))
            self.ui.catalog_table.setItem(
                i, 5, QTableWidgetItem(p['disease_group']))
            self.ui.catalog_table.setItem(
                i, 6, QTableWidgetItem(p['prescription']))

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        disease = self.ui.disease_combo.currentText()
        form = self.ui.form_combo.currentText()
        mfr = self.ui.manufacturer_combo.currentText()
        prescription = self.ui.prescription_combo.currentText()
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
        if prescription != 'Все':
            result = [p for p in result
                      if p['prescription'] == prescription]
        if p_max > 0:
            result = [p for p in result
                      if p_min <= p['price'] <= p_max]
        self.fill_catalog(result)

    def reset_search(self):
        self.ui.search_edit.clear()
        self.ui.disease_combo.setCurrentIndex(0)
        self.ui.form_combo.setCurrentIndex(0)
        self.ui.manufacturer_combo.setCurrentIndex(0)
        self.ui.prescription_combo.setCurrentIndex(0)
        self.ui.price_min.setValue(0)
        self.ui.price_max.setValue(0)
        self.fill_catalog(self.products)

    def add_to_cart(self):
        row = self.ui.catalog_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите препарат')
            return
        name = self.ui.catalog_table.item(row, 1).text()
        price = float(self.ui.catalog_table.item(row, 4).text())
        pid = None
        for p in self.products:
            if p['name'] == name and p['price'] == price:
                pid = p['id']
                break
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

    # -------------------- Корзина --------------------
    def refresh_cart(self):
        self.ui.cart_table.setRowCount(len(self.cart))
        self.ui.cart_table.setColumnCount(4)
        self.ui.cart_table.setHorizontalHeaderLabels(
            ['Наименование', 'Цена', 'Кол-во', 'Сумма'])
        total = 0
        for i, item in enumerate(self.cart):
            self.ui.cart_table.setItem(
                i, 0, QTableWidgetItem(item['name']))
            self.ui.cart_table.setItem(
                i, 1, QTableWidgetItem(f'{item["price"]} руб'))
            self.ui.cart_table.setItem(
                i, 2, QTableWidgetItem(str(item['quantity'])))
            s = item['price'] * item['quantity']
            self.ui.cart_table.setItem(
                i, 3, QTableWidgetItem(f'{s} руб'))
            total += s
        self.ui.cart_total_label.setText(f'Итого: {total} руб')

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

        # Содержимое заказа
        layout.addWidget(QLabel('Состав заказа:'))
        order_tbl = QTableWidget()
        order_tbl.setRowCount(len(self.cart))
        order_tbl.setColumnCount(4)
        order_tbl.setHorizontalHeaderLabels(
            ['Наименование', 'Цена', 'Кол-во', 'Сумма'])
        total = 0
        for i, item in enumerate(self.cart):
            order_tbl.setItem(i, 0, QTableWidgetItem(item['name']))
            order_tbl.setItem(
                i, 1, QTableWidgetItem(f'{item["price"]} руб'))
            order_tbl.setItem(
                i, 2, QTableWidgetItem(str(item['quantity'])))
            s = item['price'] * item['quantity']
            order_tbl.setItem(i, 3, QTableWidgetItem(f'{s} руб'))
            total += s
        layout.addWidget(order_tbl)

        total_label = QLabel(f'Сумма заказа: {total} руб')
        total_label.setStyleSheet('font-weight: bold; font-size: 13px;')
        layout.addWidget(total_label)

        # Контактные данные
        layout.addWidget(QLabel(
            f'Покупатель: {self.user["fio"]} | '
            f'{self.user["email"]} | {self.user["phone"]}'))

        # Способ оплаты
        pay_layout = QHBoxLayout()
        pay_layout.addWidget(QLabel('Способ оплаты:'))
        pay_combo = QComboBox()
        pay_combo.addItems(['Наличные', 'Банковская карта'])
        pay_layout.addWidget(pay_combo)
        layout.addLayout(pay_layout)

        # Адрес доставки
        addr_layout = QHBoxLayout()
        addr_layout.addWidget(QLabel('Адрес доставки:'))
        addr_combo = QComboBox()
        conn = get_connection()
        addrs = conn.execute(
            'SELECT address FROM addresses WHERE user_id = ?',
            (self.user['id'],)
        ).fetchall()
        conn.close()
        for a in addrs:
            addr_combo.addItem(a['address'])
        addr_combo.addItem('-- Новый адрес --')
        addr_layout.addWidget(addr_combo)
        layout.addLayout(addr_layout)

        new_addr_edit = QLineEdit()
        new_addr_edit.setPlaceholderText('Введите новый адрес доставки')
        new_addr_edit.setVisible(False)
        layout.addWidget(new_addr_edit)

        def on_addr_changed(idx):
            new_addr_edit.setVisible(
                addr_combo.currentText() == '-- Новый адрес --')

        addr_combo.currentIndexChanged.connect(on_addr_changed)

        # Кнопка подтверждения
        confirm_btn = QPushButton('Подтвердить заказ')
        layout.addWidget(confirm_btn)

        def confirm_order():
            address = addr_combo.currentText()
            if address == '-- Новый адрес --':
                address = new_addr_edit.text().strip()
                if not address:
                    QMessageBox.warning(
                        dlg, 'Ошибка', 'Введите адрес доставки')
                    return
                # сохраняем новый адрес
                conn = get_connection()
                conn.execute(
                    'INSERT INTO addresses (user_id, address) '
                    'VALUES (?,?)',
                    (self.user['id'], address)
                )
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
                f'Сумма: {total} руб\n'
                f'Оплата: {payment}\n'
                f'Адрес: {address}\n'
                f'Примерная дата доставки: {delivery_date}')

        confirm_btn.clicked.connect(confirm_order)
        dlg.exec()

    # -------------------- Заказы --------------------
    def refresh_orders(self):
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC',
            (self.user['id'],)
        ).fetchall()
        conn.close()

        self.ui.orders_table.setRowCount(len(rows))
        self.ui.orders_table.setColumnCount(6)
        self.ui.orders_table.setHorizontalHeaderLabels(
            ['№', 'Дата', 'Сумма', 'Оплата', 'Статус', 'Дата доставки'])
        for i, o in enumerate(rows):
            self.ui.orders_table.setItem(
                i, 0, QTableWidgetItem(str(o['id'])))
            self.ui.orders_table.setItem(
                i, 1, QTableWidgetItem(o['order_date']))
            self.ui.orders_table.setItem(
                i, 2, QTableWidgetItem(f'{o["total"]} руб'))
            self.ui.orders_table.setItem(
                i, 3, QTableWidgetItem(o['payment_method']))
            self.ui.orders_table.setItem(
                i, 4, QTableWidgetItem(o['status']))
            self.ui.orders_table.setItem(
                i, 5, QTableWidgetItem(o['delivery_date']))

        self.ui.profile_orders_count.setText(f'Заказов: {len(rows)}')

    # -------------------- Адреса --------------------
    def refresh_addresses(self):
        conn = get_connection()
        addrs = conn.execute(
            'SELECT * FROM addresses WHERE user_id = ?',
            (self.user['id'],)
        ).fetchall()
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
            'INSERT INTO addresses (user_id, address) VALUES (?,?)',
            (self.user['id'], address)
        )
        conn.commit()
        conn.close()
        self.ui.new_address_edit.clear()
        self.refresh_addresses()
        QMessageBox.information(self, 'Успех', 'Адрес добавлен')


# ============================================================
#  ЗАПУСК
# ============================================================
if __name__ == '__main__':
    # Автоматическое создание БД при первом запуске
    if not os.path.exists(DB_PATH):
        from create_data import create_database
        create_database()

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
