import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'rental.db')


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE equipment_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cur.execute('''
        CREATE TABLE pickup_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo TEXT DEFAULT '',
            equipment_type_id INTEGER NOT NULL,
            rental_price_per_day REAL DEFAULT 0,
            pickup_point_id INTEGER NOT NULL,
            available INTEGER DEFAULT 1,
            FOREIGN KEY (equipment_type_id) REFERENCES equipment_types(id),
            FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT DEFAULT '',
            password TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pickup_point_id INTEGER,
            role TEXT DEFAULT 'employee',
            FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE rental_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    cur.execute('''
        CREATE TABLE rental_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            equipment_id INTEGER NOT NULL,
            employee_id INTEGER,
            status_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_cost REAL DEFAULT 0,
            created_at TEXT DEFAULT '',
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (equipment_id) REFERENCES equipment(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (status_id) REFERENCES rental_statuses(id)
        )
    ''')

    types = ['Лыжи', 'Сноуборд', 'Коньки', 'Велосипед', 'Самокат',
             'Ракетка', 'Мяч', 'Палатка', 'Каяк', 'Спальный мешок']
    for t in types:
        cur.execute('INSERT INTO equipment_types (name) VALUES (?)', (t,))

    points = [
        ('Пункт "Спорт-Центр"', 'г. Москва, ул. Спортивная, д. 10'),
        ('Пункт "Олимп"', 'г. Москва, пр-т Вернадского, д. 55'),
        ('Пункт "Актив"', 'г. Москва, ул. Ленина, д. 3'),
    ]
    for name, addr in points:
        cur.execute(
            'INSERT INTO pickup_points (name, address) VALUES (?, ?)',
            (name, addr))

    statuses = ['Новая', 'Подтверждена', 'Выдано', 'Возвращено', 'Отклонена']
    for s in statuses:
        cur.execute(
            'INSERT INTO rental_statuses (name) VALUES (?)', (s,))

    equipment = [
        ('Лыжи горные Atomic Redster', 'photos/лыжи_atomic.jpg',
         'Лыжи', 1400, 1, 1),
        ('Лыжи беговые Rossignol X-ium', 'photos/лыжи_rossignol.jpg',
         'Лыжи', 750, 2, 1),
        ('Сноуборд Jones Mountain Twin', 'photos/сноуборд_jones.jpg',
         'Сноуборд', 1900, 1, 1),
        ('Коньки фигурные Jackson Ultima', 'photos/коньки_jackson.jpg',
         'Коньки', 650, 3, 0),
        ('Коньки хоккейные CCM Ribcor', 'photos/коньки_ccm.jpg',
         'Коньки', 750, 1, 1),
        ('Велосипед горный Merida Big.Nine', 'photos/велосипед_merida.jpg',
         'Велосипед', 1100, 2, 1),
        ('Велосипед городской Cube Hyde', 'photos/велосипед_cube.jpg',
         'Велосипед', 850, 3, 0),
        ('Самокат электрический Ninebot', 'photos/самокат_ninebot.jpg',
         'Самокат', 550, 1, 1),
        ('Ракетка теннисная Head Speed', 'photos/ракетка_head.jpg',
         'Ракетка', 350, 2, 1),
        ('Мяч футбольный Nike Flight', 'photos/мяч_nike.jpg',
         'Мяч', 250, 3, 1),
        ('Палатка 3-местная Nordway', 'photos/палатка_nordway.jpg',
         'Палатка', 1700, 1, 1),
        ('Каяк двухместный Intex Explorer', 'photos/каяк_intex.jpg',
         'Каяк', 2300, 2, 0),
    ]

    type_ids = {}
    for t in types:
        row = cur.execute(
            'SELECT id FROM equipment_types WHERE name = ?', (t,)
        ).fetchone()
        type_ids[t] = row[0]

    for eq in equipment:
        name, photo, eq_type, price, point_id, avail = eq
        cur.execute('''
            INSERT INTO equipment
                (name, photo, equipment_type_id, rental_price_per_day,
                 pickup_point_id, available)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, photo, type_ids[eq_type], price, point_id, avail))

    cur.execute('''
        INSERT INTO clients (fio, email, phone, password)
        VALUES (?, ?, ?, ?)
    ''', ('Иванов Иван Иванович', 'client@test.ru', '+79001234567', '1'))

    cur.execute('''
        INSERT INTO employees (fio, login, password, pickup_point_id, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Петров Петр Петрович', 'employee', '1', 1, 'employee'))

    cur.execute('''
        INSERT INTO employees (fio, login, password, pickup_point_id, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Сидоров Алексей Сергеевич', 'admin', '1', None, 'admin'))

    conn.commit()
    conn.close()

    print(f'База данных создана: {DB_PATH}')
    print(f'Добавлено оборудования: {len(equipment)}')
    print('Тестовые пользователи:')
    print('  Клиент: client@test.ru / 1')
    print('  Сотрудник: employee / 1')
    print('  Администратор: admin / 1')


if __name__ == '__main__':
    create_database()
