import sys
import os
import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QFont, QColor, QBrush, QIcon
from PyQt6.QtCore import Qt, QSize, QDate

from gen.auth_ui import Ui_AuthForm
from gen.main_ui import Ui_MainForm
from gen.client_ui import Ui_ClientForm
from gen.employee_ui import Ui_EmployeeForm
from gen.admin_ui import Ui_AdminForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'rental.db')

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
QLineEdit {
    padding: 6px 10px;
    border: 1px solid #D5D8DC;
    border-radius: 8px;
    background: white;
}
QLineEdit:focus { border: 2px solid #3498DB; }
QComboBox {
    padding: 6px 10px;
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
QPushButton:hover { background: #F8F9FA; border-color: #BDC3C7; }
#search_btn {
    background: #3498DB; color: white;
    border: none; font-weight: bold;
}
#search_btn:hover { background: #2E86C1; }
#auth_btn {
    background: #EBF5FB; color: #2E86C1;
    border: 1px solid #AED6F1; font-weight: bold;
}
#auth_btn:hover { background: #D4E6F1; }
#login_btn {
    background: #3498DB; color: white;
    border: none; font-weight: bold;
}
#login_btn:hover { background: #2E86C1; }
#guest_btn {
    background: #E8F8F5; color: #1ABC9C;
    border: 1px solid #A3E4D7; font-weight: bold;
}
#guest_btn:hover { background: #D1F2EB; }
#checkout_btn {
    background: #27AE60; color: white;
    border: none; border-radius: 10px;
    font-size: 14px; font-weight: bold;
}
#checkout_btn:hover { background: #2ECC71; }
#delete_btn {
    background: #E74C3C; color: white;
    border: none; font-weight: bold;
}
#delete_btn:hover { background: #EC7063; }
QTabWidget::pane { border: none; }
QTabBar::tab { padding: 10px 20px; font-size: 13px; }
QTabBar::tab:selected {
    color: #2E86C1; font-weight: bold;
    border-bottom: 2px solid #2E86C1;
}
QTableWidget {
    border: 1px solid #E8E8E8;
    border-radius: 8px;
    gridline-color: #F0F0F0;
    alternate-background-color: #FAFBFC;
}
QTableWidget::item { padding: 6px; }
QHeaderView::section {
    background: #F8F9FA; border: none;
    border-bottom: 1px solid #E8E8E8;
    padding: 8px; font-weight: bold; color: #566573;
}
"""

GRAY_BRUSH = QBrush(QColor(220, 220, 220))


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


def fill_equipment_table(table, data):
    table.verticalHeader().setDefaultSectionSize(70)
    table.setIconSize(QSize(60, 60))
    table.setRowCount(len(data))
    for i, eq in enumerate(data):
        photo_path = os.path.join(BASE_DIR, eq['photo']) \
            if eq['photo'] else ''
        if photo_path and os.path.exists(photo_path):
            pix = QPixmap(photo_path).scaled(
                60, 60,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            icon_item = QTableWidgetItem()
            icon_item.setIcon(QIcon(pix))
            table.setItem(i, 0, icon_item)
        else:
            table.setItem(i, 0, QTableWidgetItem(''))

        table.setItem(i, 1, QTableWidgetItem(eq['name']))
        table.setItem(i, 2, QTableWidgetItem(eq['type_name']))
        table.setItem(i, 3, QTableWidgetItem(
            f'{eq["rental_price_per_day"]:.0f} руб'))
        table.setItem(i, 4, QTableWidgetItem(eq['point_name']))

        avail_text = 'Доступно' if eq['available'] else 'Недоступно'
        table.setItem(i, 5, QTableWidgetItem(avail_text))

        if not eq['available']:
            for col in range(table.columnCount()):
                item = table.item(i, col)
                if item:
                    item.setBackground(GRAY_BRUSH)

    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


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

        QMessageBox.warning(
            self, 'Ошибка', 'Неверный логин или пароль')

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
        self.client_win = ClientWindow(client_dict)
        self.client_win.show()
        self.close()

    def open_employee(self, emp_dict):
        self.emp_win = EmployeeWindow(emp_dict)
        self.emp_win.show()
        self.close()

    def open_admin(self, emp_dict):
        self.admin_win = AdminWindow(emp_dict)
        self.admin_win.show()
        self.close()


class MainWindow(QWidget):
    def __init__(self, auth_window=None):
        super().__init__()
        self.ui = Ui_MainForm()
        self.ui.setupUi(self)
        self.auth_window = auth_window

        self.equipment = load_equipment()
        self.fill_filters()
        self.refresh_table(self.equipment)

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

    def refresh_table(self, data):
        fill_equipment_table(self.ui.table, data)
        self.ui.count_label.setText(f'Оборудования: {len(data)}')

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        eq_type = self.ui.type_combo.currentText()
        point = self.ui.point_combo.currentText()

        result = self.equipment
        if text:
            result = [e for e in result
                      if text in e['name'].lower()]
        if eq_type != 'Все типы':
            result = [e for e in result
                      if e['type_name'] == eq_type]
        if point != 'Все пункты':
            result = [e for e in result
                      if e['point_name'] == point]
        self.refresh_table(result)

    def reset(self):
        self.ui.search_edit.clear()
        self.ui.type_combo.setCurrentIndex(0)
        self.ui.point_combo.setCurrentIndex(0)
        self.refresh_table(self.equipment)

    def open_auth(self):
        if self.auth_window:
            self.auth_window.show()
        self.close()


class ClientWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_ClientForm()
        self.ui.setupUi(self)
        self.user = user
        self.equipment = load_equipment()

        self.fill_filters()
        self.refresh_equip(self.equipment)
        self.ui.search_btn.clicked.connect(self.search)
        self.ui.reset_btn.clicked.connect(self.reset_search)
        self.ui.rent_btn.clicked.connect(self.create_request)

        self.refresh_requests()

        self.ui.profile_fio.setText(f'ФИО: {self.user["fio"]}')
        self.ui.profile_email.setText(
            f'E-mail: {self.user["email"]}')
        self.ui.profile_phone.setText(
            f'Телефон: {self.user["phone"]}')

    def fill_filters(self):
        self.ui.type_combo.clear()
        self.ui.type_combo.addItem('Все типы')
        self.ui.type_combo.addItems(load_types())

        self.ui.point_combo.clear()
        self.ui.point_combo.addItem('Все пункты')
        for p in load_points():
            self.ui.point_combo.addItem(p['name'])

    def refresh_equip(self, data):
        fill_equipment_table(self.ui.equip_table, data)

    def search(self):
        text = self.ui.search_edit.text().strip().lower()
        eq_type = self.ui.type_combo.currentText()
        point = self.ui.point_combo.currentText()

        result = self.equipment
        if text:
            result = [e for e in result
                      if text in e['name'].lower()]
        if eq_type != 'Все типы':
            result = [e for e in result
                      if e['type_name'] == eq_type]
        if point != 'Все пункты':
            result = [e for e in result
                      if e['point_name'] == point]
        self.refresh_equip(result)

    def reset_search(self):
        self.ui.search_edit.clear()
        self.ui.type_combo.setCurrentIndex(0)
        self.ui.point_combo.setCurrentIndex(0)
        self.refresh_equip(self.equipment)

    def create_request(self):
        row = self.ui.equip_table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, 'Внимание',
                'Выберите оборудование из таблицы')
            return

        name_item = self.ui.equip_table.item(row, 1)
        if not name_item:
            return
        eq_name = name_item.text()
        eq = next((e for e in self.equipment
                    if e['name'] == eq_name), None)
        if not eq:
            return

        if not eq['available']:
            QMessageBox.warning(
                self, 'Внимание',
                'Это оборудование сейчас недоступно для аренды')
            return

        dlg = QDialog(self)
        dlg.setWindowTitle('Оформление заявки на аренду')
        dlg.resize(400, 300)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel(
            f'Оборудование: {eq["name"]}'))
        layout.addWidget(QLabel(
            f'Тип: {eq["type_name"]}'))
        layout.addWidget(QLabel(
            f'Пункт выдачи: {eq["point_name"]}'))
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
            'font-weight: bold; font-size: 14px; color: #27AE60;')
        layout.addWidget(total_label)

        def calc_total():
            days = start_date.date().daysTo(end_date.date())
            if days < 1:
                days = 1
            cost = days * eq['rental_price_per_day']
            total_label.setText(
                f'Итого: {cost:.0f} руб ({days} сут.)')

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
            status_id = status['id']

            conn.execute('''
                INSERT INTO rental_requests
                    (client_id, equipment_id, status_id,
                     start_date, end_date, total_cost, created_at)
                VALUES (?,?,?,?,?,?,?)
            ''', (self.user['id'], eq['id'], status_id,
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
        self.ui.profile_requests_count.setText(
            f'Заявок: {len(rows)}')


class EmployeeWindow(QWidget):
    def __init__(self, employee):
        super().__init__()
        self.ui = Ui_EmployeeForm()
        self.ui.setupUi(self)
        self.employee = employee

        self.ui.employee_label.setText(
            f'Сотрудник: {self.employee["fio"]}')

        self.statuses = load_statuses()
        self.ui.status_filter_combo.addItem('Все статусы')
        for s in self.statuses:
            self.ui.status_filter_combo.addItem(s['name'])

        for s in self.statuses:
            self.ui.status_combo.addItem(s['name'])

        self.refresh_requests()

        self.ui.refresh_btn.clicked.connect(self.refresh_requests)
        self.ui.status_filter_combo.currentIndexChanged.connect(
            self.refresh_requests)
        self.ui.change_status_btn.clicked.connect(self.change_status)

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
            tbl.setItem(i, 8, QTableWidgetItem(
                r['emp_fio'] or ''))

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

        self.refresh_requests()
        QMessageBox.information(
            self, 'Статус обновлен',
            f'Заявка #{request_id}: {new_status_name}')


class AdminWindow(QWidget):
    def __init__(self, employee):
        super().__init__()
        self.ui = Ui_AdminForm()
        self.ui.setupUi(self)
        self.employee = employee

        self.refresh_table()

        self.ui.add_btn.clicked.connect(self.add_equipment)
        self.ui.edit_btn.clicked.connect(self.edit_equipment)
        self.ui.delete_btn.clicked.connect(self.delete_equipment)
        self.ui.refresh_btn.clicked.connect(self.refresh_table)

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
                for col in range(tbl.columnCount()):
                    item = tbl.item(i, col)
                    if item:
                        item.setBackground(GRAY_BRUSH)

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


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from create_data import create_database
        create_database()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    w = AuthWindow()
    w.show()
    sys.exit(app.exec())
