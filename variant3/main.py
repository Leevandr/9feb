import sys
import os
import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QFont, QColor, QBrush
from PyQt6.QtCore import Qt, QDate

from gen.auth_ui import Ui_AuthForm
from gen.main_ui import Ui_MainForm
from gen.client_ui import Ui_ClientForm
from gen.employee_ui import Ui_EmployeeForm
from gen.admin_ui import Ui_AdminForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'rental.db')

NAV_STYLE = (
    'text-align:left;padding:10px 14px;border:none;border-radius:4px;'
    'background:transparent;color:#CCCCCC;font-size:13px;'
)
NAV_ACTIVE = (
    'text-align:left;padding:10px 14px;border:none;border-radius:4px;'
    'background:#3D3D3D;color:#F5A623;font-weight:bold;font-size:13px;'
)

APP_STYLE = """
QWidget { font-family: 'Segoe UI','Roboto','Arial',sans-serif; font-size:13px; }
#sidebar { background:#2C2C2C; border-right:none; }
#sidebar QLabel { color:#EEEEEE; }
#header_panel { background:#FAFAFA; border-bottom:1px solid #DDD; }
#filter_panel { background:#FAFAFA; border-bottom:1px solid #DDD; }
#bottom_panel { background:#FAFAFA; border-top:1px solid #DDD; }
#toolbar_panel { background:#FAFAFA; border-bottom:1px solid #DDD; }
QLineEdit {
    padding:5px 10px; border:1px solid #CCC;
    border-radius:4px; background:white;
}
QLineEdit:focus { border:1px solid #E67E22; }
QComboBox {
    padding:5px 10px; border:1px solid #CCC;
    border-radius:4px; background:white;
}
QPushButton {
    padding:5px 12px; border:1px solid #CCC;
    border-radius:4px; background:#FAFAFA; color:#333;
}
QPushButton:hover { background:#F0F0F0; border-color:#AAA; }
#search_btn { background:#E67E22; color:white; border:none; }
#search_btn:hover { background:#D35400; }
#auth_btn {
    background:#FFF3E0; color:#E65100;
    border:1px solid #FFCC80;
}
#auth_btn:hover { background:#FFE0B2; }
#login_btn { background:#E67E22; color:white; border:none; }
#login_btn:hover { background:#D35400; }
#guest_btn {
    background:#F5F5F5; color:#555;
    border:1px solid #CCC;
}
#guest_btn:hover { background:#EEEEEE; }
#checkout_btn, #card_rent_btn {
    background:#E67E22; color:white; border:none;
    border-radius:4px;
}
#checkout_btn:hover, #card_rent_btn:hover { background:#D35400; }
#card_rent_btn:disabled { background:#CCC; color:#888; }
#delete_btn { background:#C0392B; color:white; border:none; }
#delete_btn:hover { background:#E74C3C; }
QTableWidget {
    border:1px solid #DDD; border-radius:4px;
    gridline-color:#EEE; alternate-background-color:#FAFAFA;
}
QTableWidget::item { padding:5px; }
QHeaderView::section {
    background:#F5F5F5; border:none;
    border-bottom:1px solid #DDD;
    padding:7px; font-weight:bold; color:#555;
}
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def load_equipment():
    conn = get_connection()
    rows = conn.execute('''
        SELECT e.id, e.name, e.photo, et.name AS type_name,
               e.rental_price_per_day, pp.name AS point_name,
               e.available, e.equipment_type_id, e.pickup_point_id
        FROM equipment e
        JOIN equipment_types et ON e.equipment_type_id = et.id
        JOIN pickup_points pp ON e.pickup_point_id = pp.id
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_types():
    conn = get_connection()
    rows = conn.execute(
        'SELECT name FROM equipment_types ORDER BY name').fetchall()
    conn.close()
    return [r['name'] for r in rows]


def load_points():
    conn = get_connection()
    rows = conn.execute(
        'SELECT id, name FROM pickup_points ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_statuses():
    conn = get_connection()
    rows = conn.execute(
        'SELECT id, name FROM rental_statuses').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_active_nav(active_btn, all_btns):
    for btn in all_btns:
        btn.setStyleSheet(NAV_STYLE)
    active_btn.setStyleSheet(NAV_ACTIVE)


def create_card(eq, on_rent=None):
    card = QFrame()
    card.setObjectName('equip_card')
    card.setFixedWidth(240)
    if eq['available']:
        card.setStyleSheet(
            '#equip_card{background:white;border:1px solid #DDD;'
            'border-radius:6px;}')
    else:
        card.setStyleSheet(
            '#equip_card{background:#EBEBEB;border:1px solid #CCC;'
            'border-radius:6px;}')

    lay = QVBoxLayout(card)
    lay.setSpacing(4)
    lay.setContentsMargins(10, 10, 10, 10)

    img_label = QLabel()
    img_label.setFixedSize(220, 140)
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    img_label.setStyleSheet('background:#F0F0F0;border-radius:4px;')
    photo_path = os.path.join(BASE_DIR, eq['photo']) if eq['photo'] else ''
    if photo_path and os.path.exists(photo_path):
        pix = QPixmap(photo_path).scaled(
            220, 140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        img_label.setPixmap(pix)
    lay.addWidget(img_label)

    name_label = QLabel(eq['name'])
    name_label.setFont(QFont('', 11, QFont.Weight.Bold))
    name_label.setWordWrap(True)
    lay.addWidget(name_label)

    price_label = QLabel(f'{eq["rental_price_per_day"]:.0f} ₽/сутки')
    price_label.setStyleSheet('color:#E67E22;font-size:12px;font-weight:bold;')
    lay.addWidget(price_label)

    point_label = QLabel(f'▶ {eq["point_name"]}')
    point_label.setStyleSheet('color:#777;font-size:11px;')
    lay.addWidget(point_label)

    if eq['available']:
        avail_label = QLabel('В наличии')
        avail_label.setStyleSheet('color:#2E7D32;font-size:11px;')
    else:
        avail_label = QLabel('Нет в наличии')
        avail_label.setStyleSheet('color:#C62828;font-size:11px;')
    lay.addWidget(avail_label)

    if on_rent is not None:
        rent_btn = QPushButton('Оформить аренду')
        rent_btn.setObjectName('card_rent_btn')
        rent_btn.setMinimumHeight(32)
        if not eq['available']:
            rent_btn.setEnabled(False)
        rent_btn.clicked.connect(lambda checked, e=eq: on_rent(e))
        lay.addWidget(rent_btn)

    return card


def fill_catalog(scroll_area, data, on_rent=None):
    container = QWidget()
    grid = QGridLayout(container)
    grid.setSpacing(15)
    grid.setContentsMargins(15, 5, 15, 15)
    cols = 3
    for i, eq in enumerate(data):
        card = create_card(eq, on_rent)
        grid.addWidget(card, i // cols, i % cols)
    grid.setRowStretch(len(data) // cols + 1, 1)
    scroll_area.setWidget(container)


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AuthForm()
        self.ui.setupUi(self)
        self.ui.login_btn.clicked.connect(self.do_login)
        self.ui.guest_btn.clicked.connect(self.open_guest)
        self.ui.register_btn.clicked.connect(self.do_register)

    def do_login(self):
        login = self.ui.login_edit.text().strip()
        password = self.ui.login_password_edit.text().strip()
        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        conn = get_connection()
        emp = conn.execute(
            'SELECT * FROM employees WHERE login = ? AND password = ?',
            (login, password)).fetchone()
        if emp:
            conn.close()
            emp_dict = dict(emp)
            if emp_dict['role'] == 'admin':
                self.open_admin(emp_dict)
            else:
                self.open_employee(emp_dict)
            return
        client = conn.execute(
            'SELECT * FROM clients WHERE email = ? AND password = ?',
            (login, password)).fetchone()
        conn.close()
        if client:
            self.open_client(dict(client))
            return
        QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

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
            'SELECT id FROM clients WHERE email = ?', (email,)
        ).fetchone()
        if existing:
            conn.close()
            QMessageBox.warning(
                self, 'Ошибка',
                'Клиент с таким e-mail уже существует')
            return
        conn.execute(
            'INSERT INTO clients (fio, email, phone, password) '
            'VALUES (?,?,?,?)',
            (fio, email, phone, pwd))
        conn.commit()
        client = conn.execute(
            'SELECT * FROM clients WHERE email = ?', (email,)
        ).fetchone()
        conn.close()
        QMessageBox.information(
            self, 'Успех', 'Регистрация прошла успешно!')
        self.open_client(dict(client))

    def open_guest(self):
        self.main_win = MainWindow(auth_window=self)
        self.main_win.show()
        self.hide()

    def open_client(self, client_dict):
        self.client_win = ClientWindow(client_dict, auth_window=self)
        self.client_win.show()
        self.hide()

    def open_employee(self, emp_dict):
        self.emp_win = EmployeeWindow(emp_dict, auth_window=self)
        self.emp_win.show()
        self.hide()

    def open_admin(self, emp_dict):
        self.admin_win = AdminWindow(emp_dict, auth_window=self)
        self.admin_win.show()
        self.hide()


class MainWindow(QWidget):
    def __init__(self, auth_window=None):
        super().__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)
        self.auth_window = auth_window
        self.equipment = load_equipment()

        set_active_nav(self.ui.nav_catalog_btn, [self.ui.nav_catalog_btn])
        self.fill_filters()
        self.refresh_catalog(self.equipment)

        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset)
        self.ui.auth_btn.clicked.connect(self.open_auth)

    def fill_filters(self):
        self.ui.type_combo.clear()
        self.ui.type_combo.addItem('Все типы')
        self.ui.type_combo.addItems(load_types())
        self.ui.point_combo.clear()
        self.ui.point_combo.addItem('Все пункты')
        for p in load_points():
            self.ui.point_combo.addItem(p['name'])

    def refresh_catalog(self, data):
        fill_catalog(self.ui.catalog_scroll, data)
        self.ui.count_label.setText(f'Оборудования: {len(data)}')

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        eq_type = self.ui.type_combo.currentText()
        point = self.ui.point_combo.currentText()
        result = self.equipment
        if text:
            result = [e for e in result if text in e['name'].lower()]
        if eq_type != 'Все типы':
            result = [e for e in result if e['type_name'] == eq_type]
        if point != 'Все пункты':
            result = [e for e in result if e['point_name'] == point]
        self.refresh_catalog(result)

    def reset(self):
        self.ui.search_edit.clear()
        self.ui.type_combo.setCurrentIndex(0)
        self.ui.point_combo.setCurrentIndex(0)
        self.refresh_catalog(self.equipment)

    def open_auth(self):
        if self.auth_window:
            self.auth_window.show()
        self.close()


class ClientWindow(QWidget):
    def __init__(self, user, auth_window=None):
        super().__init__()
        self.ui = Ui_ClientForm()
        self.ui.setupUi(self)
        self.user = user
        self.auth_window = auth_window
        self.equipment = load_equipment()

        self.nav_btns = [
            self.ui.nav_catalog_btn,
            self.ui.nav_requests_btn,
            self.ui.nav_profile_btn,
        ]

        self.ui.welcome_label.setText(
            f'Добро пожаловать, {self.user["fio"]}')

        self.fill_filters()
        self.show_catalog()

        self.ui.nav_catalog_btn.clicked.connect(self.show_catalog)
        self.ui.nav_requests_btn.clicked.connect(self.show_requests)
        self.ui.nav_profile_btn.clicked.connect(self.show_profile)
        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset_search)
        self.ui.back_btn.clicked.connect(self.go_back)
        self.ui.logout_btn.clicked.connect(self.go_back)

    def fill_filters(self):
        self.ui.type_combo.clear()
        self.ui.type_combo.addItem('Все типы')
        self.ui.type_combo.addItems(load_types())
        self.ui.point_combo.clear()
        self.ui.point_combo.addItem('Все пункты')
        for p in load_points():
            self.ui.point_combo.addItem(p['name'])

    def show_catalog(self):
        self.ui.pages.setCurrentIndex(0)
        set_active_nav(self.ui.nav_catalog_btn, self.nav_btns)
        self.refresh_catalog(self.equipment)

    def show_requests(self):
        self.ui.pages.setCurrentIndex(1)
        set_active_nav(self.ui.nav_requests_btn, self.nav_btns)
        self.refresh_requests()

    def show_profile(self):
        self.ui.pages.setCurrentIndex(2)
        set_active_nav(self.ui.nav_profile_btn, self.nav_btns)
        self.ui.profile_fio.setText(f'ФИО: {self.user["fio"]}')
        self.ui.profile_email.setText(f'E-mail: {self.user["email"]}')
        self.ui.profile_phone.setText(f'Телефон: {self.user["phone"]}')

    def refresh_catalog(self, data):
        fill_catalog(self.ui.catalog_scroll, data,
                     on_rent=self.create_request)

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        eq_type = self.ui.type_combo.currentText()
        point = self.ui.point_combo.currentText()
        result = self.equipment
        if text:
            result = [e for e in result if text in e['name'].lower()]
        if eq_type != 'Все типы':
            result = [e for e in result if e['type_name'] == eq_type]
        if point != 'Все пункты':
            result = [e for e in result if e['point_name'] == point]
        self.refresh_catalog(result)

    def reset_search(self):
        self.ui.search_edit.clear()
        self.ui.type_combo.setCurrentIndex(0)
        self.ui.point_combo.setCurrentIndex(0)
        self.refresh_catalog(self.equipment)

    def create_request(self, eq):
        if not eq['available']:
            QMessageBox.warning(
                self, 'Внимание',
                'Это оборудование сейчас недоступно для аренды')
            return

        dlg = QDialog(self)
        dlg.setWindowTitle('Оформление заявки на аренду')
        dlg.resize(400, 300)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel(f'Оборудование: {eq["name"]}'))
        layout.addWidget(QLabel(f'Тип: {eq["type_name"]}'))
        layout.addWidget(QLabel(f'Пункт выдачи: {eq["point_name"]}'))
        layout.addWidget(QLabel(
            f'Стоимость: {eq["rental_price_per_day"]:.0f} руб/сутки'))

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('С:'))
        start_date = QDateEdit(dlg)
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate())
        start_date.setMinimumDate(QDate.currentDate())
        date_layout.addWidget(start_date)

        date_layout.addWidget(QLabel('По:'))
        end_date = QDateEdit(dlg)
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate().addDays(3))
        end_date.setMinimumDate(QDate.currentDate().addDays(1))
        date_layout.addWidget(end_date)
        layout.addLayout(date_layout)

        total_label = QLabel('')
        total_label.setStyleSheet(
            'font-weight:bold;font-size:14px;color:#E67E22;')
        layout.addWidget(total_label)

        def calc_total():
            days = start_date.date().daysTo(end_date.date())
            if days < 1:
                days = 1
            cost = days * eq['rental_price_per_day']
            total_label.setText(f'Итого: {cost:.0f} руб ({days} сут.)')

        start_date.dateChanged.connect(calc_total)
        end_date.dateChanged.connect(calc_total)
        calc_total()

        confirm_btn = QPushButton('Подтвердить заявку')
        confirm_btn.setObjectName('checkout_btn')
        confirm_btn.setMinimumHeight(40)
        layout.addWidget(confirm_btn)

        def confirm():
            days = start_date.date().daysTo(end_date.date())
            if days < 1:
                QMessageBox.warning(
                    dlg, 'Ошибка',
                    'Дата окончания должна быть позже даты начала')
                return
            cost = days * eq['rental_price_per_day']
            s_date = start_date.date().toString('yyyy-MM-dd')
            e_date = end_date.date().toString('yyyy-MM-dd')
            created = datetime.now().strftime('%Y-%m-%d %H:%M')

            conn = get_connection()
            status = conn.execute(
                "SELECT id FROM rental_statuses WHERE name = 'Новая'"
            ).fetchone()

            conn.execute('''
                INSERT INTO rental_requests
                    (client_id, equipment_id, status_id,
                     start_date, end_date, total_cost, created_at)
                VALUES (?,?,?,?,?,?,?)
            ''', (self.user['id'], eq['id'], status['id'],
                  s_date, e_date, cost, created))
            conn.commit()
            conn.close()

            dlg.accept()
            self.refresh_requests()
            QMessageBox.information(
                self, 'Заявка оформлена',
                f'Оборудование: {eq["name"]}\n'
                f'Период: {s_date} — {e_date}\n'
                f'Стоимость: {cost:.0f} руб')

        confirm_btn.clicked.connect(confirm)
        dlg.exec()

    def refresh_requests(self):
        conn = get_connection()
        rows = conn.execute('''
            SELECT rr.id, e.name AS equip_name,
                   rs.name AS status_name,
                   rr.start_date, rr.end_date,
                   rr.total_cost, rr.created_at
            FROM rental_requests rr
            JOIN equipment e ON rr.equipment_id = e.id
            JOIN rental_statuses rs ON rr.status_id = rs.id
            WHERE rr.client_id = ?
            ORDER BY rr.id DESC
        ''', (self.user['id'],)).fetchall()
        conn.close()

        tbl = self.ui.requests_table
        tbl.setColumnCount(7)
        tbl.setHorizontalHeaderLabels(
            ['#', 'Оборудование', 'Статус', 'С', 'По',
             'Стоимость', 'Дата заявки'])
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setAlternatingRowColors(True)
        tbl.setRowCount(len(rows))

        for i, r in enumerate(rows):
            tbl.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            tbl.setItem(i, 1, QTableWidgetItem(r['equip_name']))
            tbl.setItem(i, 2, QTableWidgetItem(r['status_name']))
            tbl.setItem(i, 3, QTableWidgetItem(r['start_date']))
            tbl.setItem(i, 4, QTableWidgetItem(r['end_date']))
            tbl.setItem(i, 5, QTableWidgetItem(
                f'{r["total_cost"]:.0f} руб'))
            tbl.setItem(i, 6, QTableWidgetItem(r['created_at']))

        tbl.resizeColumnsToContents()
        self.ui.profile_requests_count.setText(f'Заявок: {len(rows)}')

    def go_back(self):
        if self.auth_window:
            self.auth_window.show()
        self.close()


class EmployeeWindow(QWidget):
    def __init__(self, employee, auth_window=None):
        super().__init__()
        self.ui = Ui_EmployeeForm()
        self.ui.setupUi(self)
        self.employee = employee
        self.auth_window = auth_window
        self.equipment = load_equipment()

        self.nav_btns = [
            self.ui.nav_catalog_btn,
            self.ui.nav_requests_btn,
        ]

        self.ui.welcome_label.setText(
            f'Добро пожаловать, {self.employee["fio"]}')

        self.statuses = load_statuses()
        self.ui.status_filter_combo.addItem('Все статусы')
        for s in self.statuses:
            self.ui.status_filter_combo.addItem(s['name'])
        for s in self.statuses:
            self.ui.status_combo.addItem(s['name'])

        self.fill_filters()
        self.show_requests()

        self.ui.nav_catalog_btn.clicked.connect(self.show_catalog)
        self.ui.nav_requests_btn.clicked.connect(self.show_requests)
        self.ui.refresh_btn.clicked.connect(self.refresh_requests)
        self.ui.status_filter_combo.currentIndexChanged.connect(
            self.refresh_requests)
        self.ui.change_status_btn.clicked.connect(self.change_status)
        self.ui.search_btn.clicked.connect(self.search_catalog)
        self.ui.reset_btn.clicked.connect(self.reset_catalog)
        self.ui.back_btn.clicked.connect(self.go_back)
        self.ui.logout_btn.clicked.connect(self.go_back)

    def fill_filters(self):
        self.ui.type_combo.clear()
        self.ui.type_combo.addItem('Все типы')
        self.ui.type_combo.addItems(load_types())
        self.ui.point_combo.clear()
        self.ui.point_combo.addItem('Все пункты')
        for p in load_points():
            self.ui.point_combo.addItem(p['name'])

    def show_catalog(self):
        self.ui.pages.setCurrentIndex(0)
        set_active_nav(self.ui.nav_catalog_btn, self.nav_btns)
        self.refresh_catalog(self.equipment)

    def show_requests(self):
        self.ui.pages.setCurrentIndex(1)
        set_active_nav(self.ui.nav_requests_btn, self.nav_btns)
        self.refresh_requests()

    def refresh_catalog(self, data):
        fill_catalog(self.ui.catalog_scroll, data)

    def search_catalog(self):
        text = self.ui.search_edit.text().strip().lower()
        eq_type = self.ui.type_combo.currentText()
        point = self.ui.point_combo.currentText()
        result = self.equipment
        if text:
            result = [e for e in result if text in e['name'].lower()]
        if eq_type != 'Все типы':
            result = [e for e in result if e['type_name'] == eq_type]
        if point != 'Все пункты':
            result = [e for e in result if e['point_name'] == point]
        self.refresh_catalog(result)

    def reset_catalog(self):
        self.ui.search_edit.clear()
        self.ui.type_combo.setCurrentIndex(0)
        self.ui.point_combo.setCurrentIndex(0)
        self.refresh_catalog(self.equipment)

    def refresh_requests(self):
        conn = get_connection()
        status_filter = self.ui.status_filter_combo.currentText()

        if status_filter == 'Все статусы':
            rows = conn.execute('''
                SELECT rr.id, c.fio AS client_fio,
                       e.name AS equip_name,
                       rs.name AS status_name,
                       rr.start_date, rr.end_date,
                       rr.total_cost, rr.created_at,
                       emp.fio AS emp_fio
                FROM rental_requests rr
                JOIN clients c ON rr.client_id = c.id
                JOIN equipment e ON rr.equipment_id = e.id
                JOIN rental_statuses rs ON rr.status_id = rs.id
                LEFT JOIN employees emp ON rr.employee_id = emp.id
                ORDER BY rr.id DESC
            ''').fetchall()
        else:
            rows = conn.execute('''
                SELECT rr.id, c.fio AS client_fio,
                       e.name AS equip_name,
                       rs.name AS status_name,
                       rr.start_date, rr.end_date,
                       rr.total_cost, rr.created_at,
                       emp.fio AS emp_fio
                FROM rental_requests rr
                JOIN clients c ON rr.client_id = c.id
                JOIN equipment e ON rr.equipment_id = e.id
                JOIN rental_statuses rs ON rr.status_id = rs.id
                LEFT JOIN employees emp ON rr.employee_id = emp.id
                WHERE rs.name = ?
                ORDER BY rr.id DESC
            ''', (status_filter,)).fetchall()
        conn.close()

        tbl = self.ui.requests_table
        tbl.setColumnCount(9)
        tbl.setHorizontalHeaderLabels(
            ['#', 'Клиент', 'Оборудование', 'Статус',
             'С', 'По', 'Стоимость', 'Дата заявки', 'Сотрудник'])
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.setRowCount(len(rows))

        for i, r in enumerate(rows):
            tbl.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            tbl.setItem(i, 1, QTableWidgetItem(r['client_fio']))
            tbl.setItem(i, 2, QTableWidgetItem(r['equip_name']))
            tbl.setItem(i, 3, QTableWidgetItem(r['status_name']))
            tbl.setItem(i, 4, QTableWidgetItem(r['start_date']))
            tbl.setItem(i, 5, QTableWidgetItem(r['end_date']))
            tbl.setItem(i, 6, QTableWidgetItem(
                f'{r["total_cost"]:.0f} руб'))
            tbl.setItem(i, 7, QTableWidgetItem(r['created_at']))
            tbl.setItem(i, 8, QTableWidgetItem(r['emp_fio'] or ''))

        tbl.resizeColumnsToContents()

    def change_status(self):
        row = self.ui.requests_table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, 'Внимание', 'Выберите заявку')
            return

        request_id = int(
            self.ui.requests_table.item(row, 0).text())
        new_status_name = self.ui.status_combo.currentText()

        new_status = next(
            (s for s in self.statuses
             if s['name'] == new_status_name), None)
        if not new_status:
            return

        conn = get_connection()

        req = conn.execute(
            'SELECT equipment_id FROM rental_requests WHERE id = ?',
            (request_id,)).fetchone()

        conn.execute('''
            UPDATE rental_requests
            SET status_id = ?, employee_id = ?
            WHERE id = ?
        ''', (new_status['id'], self.employee['id'], request_id))

        if new_status_name == 'Выдано':
            conn.execute(
                'UPDATE equipment SET available = 0 WHERE id = ?',
                (req['equipment_id'],))
        elif new_status_name == 'Возвращено':
            conn.execute(
                'UPDATE equipment SET available = 1 WHERE id = ?',
                (req['equipment_id'],))

        conn.commit()
        conn.close()

        self.equipment = load_equipment()
        self.refresh_requests()
        QMessageBox.information(
            self, 'Статус обновлен',
            f'Заявка #{request_id}: {new_status_name}')

    def go_back(self):
        if self.auth_window:
            self.auth_window.show()
        self.close()


class AdminWindow(QWidget):
    def __init__(self, employee, auth_window=None):
        super().__init__()
        self.ui = Ui_AdminForm()
        self.ui.setupUi(self)
        self.employee = employee
        self.auth_window = auth_window

        set_active_nav(
            self.ui.nav_equipment_btn, [self.ui.nav_equipment_btn])

        self.ui.welcome_label.setText(
            f'Добро пожаловать, {self.employee["fio"]}')

        self.refresh_table()

        self.ui.add_btn.clicked.connect(self.add_equipment)
        self.ui.edit_btn.clicked.connect(self.edit_equipment)
        self.ui.delete_btn.clicked.connect(self.delete_equipment)
        self.ui.refresh_btn.clicked.connect(self.refresh_table)
        self.ui.back_btn.clicked.connect(self.go_back)
        self.ui.logout_btn.clicked.connect(self.go_back)

    def refresh_table(self):
        self.equipment = load_equipment()
        tbl = self.ui.table
        tbl.setRowCount(len(self.equipment))

        for i, eq in enumerate(self.equipment):
            tbl.setItem(i, 0, QTableWidgetItem(str(eq['id'])))
            tbl.setItem(i, 1, QTableWidgetItem(eq['name']))
            tbl.setItem(i, 2, QTableWidgetItem(eq['type_name']))
            tbl.setItem(i, 3, QTableWidgetItem(
                f'{eq["rental_price_per_day"]:.0f} руб'))
            tbl.setItem(i, 4, QTableWidgetItem(eq['point_name']))
            avail = 'Доступно' if eq['available'] else 'Недоступно'
            tbl.setItem(i, 5, QTableWidgetItem(avail))
            tbl.setItem(i, 6, QTableWidgetItem(eq['photo']))

            if not eq['available']:
                gray = QBrush(QColor(220, 220, 220))
                for col in range(tbl.columnCount()):
                    item = tbl.item(i, col)
                    if item:
                        item.setBackground(gray)

        tbl.resizeColumnsToContents()
        self.ui.count_label.setText(
            f'Оборудования: {len(self.equipment)}')

    def _equipment_dialog(self, title, eq=None):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(400, 320)
        layout = QFormLayout(dlg)

        name_edit = QLineEdit(dlg)
        if eq:
            name_edit.setText(eq['name'])
        layout.addRow('Наименование:', name_edit)

        type_combo = QComboBox(dlg)
        types = load_types()
        type_combo.addItems(types)
        if eq:
            idx = types.index(eq['type_name']) \
                if eq['type_name'] in types else 0
            type_combo.setCurrentIndex(idx)
        layout.addRow('Тип:', type_combo)

        price_spin = QDoubleSpinBox(dlg)
        price_spin.setMaximum(999999)
        price_spin.setSuffix(' руб')
        if eq:
            price_spin.setValue(eq['rental_price_per_day'])
        layout.addRow('Стоимость/сутки:', price_spin)

        point_combo = QComboBox(dlg)
        points = load_points()
        for p in points:
            point_combo.addItem(p['name'], p['id'])
        if eq:
            for j in range(point_combo.count()):
                if point_combo.itemData(j) == eq['pickup_point_id']:
                    point_combo.setCurrentIndex(j)
                    break
        layout.addRow('Пункт выдачи:', point_combo)

        avail_check = QCheckBox('Доступно для аренды', dlg)
        avail_check.setChecked(
            eq['available'] if eq else True)
        layout.addRow(avail_check)

        photo_edit = QLineEdit(dlg)
        photo_edit.setPlaceholderText('photos/filename.jpg')
        if eq:
            photo_edit.setText(eq['photo'])
        layout.addRow('Фото (путь):', photo_edit)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, dlg)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text().strip()
            if not name:
                QMessageBox.warning(
                    self, 'Ошибка', 'Введите наименование')
                return None
            conn = get_connection()
            t = conn.execute(
                'SELECT id FROM equipment_types WHERE name = ?',
                (type_combo.currentText(),)).fetchone()
            conn.close()

            return {
                'name': name,
                'equipment_type_id': t['id'],
                'rental_price_per_day': price_spin.value(),
                'pickup_point_id': point_combo.currentData(),
                'available': 1 if avail_check.isChecked() else 0,
                'photo': photo_edit.text().strip(),
            }
        return None

    def add_equipment(self):
        data = self._equipment_dialog('Добавить оборудование')
        if not data:
            return
        conn = get_connection()
        conn.execute('''
            INSERT INTO equipment
                (name, equipment_type_id, rental_price_per_day,
                 pickup_point_id, available, photo)
            VALUES (?,?,?,?,?,?)
        ''', (data['name'], data['equipment_type_id'],
              data['rental_price_per_day'],
              data['pickup_point_id'],
              data['available'], data['photo']))
        conn.commit()
        conn.close()
        self.refresh_table()
        QMessageBox.information(
            self, 'Успех', f'{data["name"]} добавлено')

    def edit_equipment(self):
        row = self.ui.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, 'Внимание', 'Выберите оборудование')
            return
        eq = self.equipment[row]
        data = self._equipment_dialog(
            'Редактировать оборудование', eq)
        if not data:
            return
        conn = get_connection()
        conn.execute('''
            UPDATE equipment
            SET name = ?, equipment_type_id = ?,
                rental_price_per_day = ?,
                pickup_point_id = ?, available = ?, photo = ?
            WHERE id = ?
        ''', (data['name'], data['equipment_type_id'],
              data['rental_price_per_day'],
              data['pickup_point_id'],
              data['available'], data['photo'], eq['id']))
        conn.commit()
        conn.close()
        self.refresh_table()
        QMessageBox.information(
            self, 'Успех', f'{data["name"]} обновлено')

    def delete_equipment(self):
        row = self.ui.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, 'Внимание', 'Выберите оборудование')
            return
        eq = self.equipment[row]
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f'Удалить "{eq["name"]}"?',
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        conn = get_connection()
        conn.execute(
            'DELETE FROM equipment WHERE id = ?', (eq['id'],))
        conn.commit()
        conn.close()
        self.refresh_table()
        QMessageBox.information(
            self, 'Удалено', f'{eq["name"]} удалено')

    def go_back(self):
        if self.auth_window:
            self.auth_window.show()
        self.close()


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from create_data import create_database
        create_database()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    w = AuthWindow()
    w.show()
    sys.exit(app.exec())
