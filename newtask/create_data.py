"""
Скрипт инициализации базы данных магазина канцелярии.
Создаёт SQLite-базу shop.db с таблицами и тестовыми данными.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'shop.db')


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------- Таблица товаров ----------
    cur.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo TEXT DEFAULT '',
            material TEXT DEFAULT '',
            price REAL DEFAULT 0,
            manufacturer TEXT DEFAULT '',
            category TEXT DEFAULT '',
            purpose TEXT DEFAULT ''
        )
    ''')

    # ---------- Таблица пользователей ----------
    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT DEFAULT '',
            password TEXT NOT NULL
        )
    ''')

    # ---------- Таблица адресов ----------
    cur.execute('''
        CREATE TABLE addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---------- Таблица заказов ----------
    cur.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_method TEXT DEFAULT 'Наличные',
            delivery_address TEXT DEFAULT '',
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Новый',
            order_date TEXT DEFAULT '',
            delivery_date TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---------- Таблица позиций заказа ----------
    cur.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # ========== Тестовые данные ==========

    products = [
        ('Ручка шариковая синяя', 'photos/pen_ball.jpg', 'Пластик', 50,
         'BIC', 'Ручки', 'Офисные принадлежности'),
        ('Ручка гелевая чёрная', 'photos/pen_gel.jpg', 'Пластик', 80,
         'Pilot', 'Ручки', 'Для школьников'),
        ('Ручка перьевая', 'photos/pen_fountain.jpg', 'Металл', 500,
         'Parker', 'Ручки', 'Офисные принадлежности'),
        ('Карандаш чернографитный HB', 'photos/pencil_hb.jpg', 'Дерево', 30,
         'KOH-I-NOOR', 'Карандаши', 'Художественные материалы'),
        ('Набор цветных карандашей 24 шт', 'photos/pencil_color.jpg', 'Дерево', 250,
         'Faber-Castell', 'Карандаши', 'Художественные материалы'),
        ('Блокнот А5 в клетку', 'photos/notebook_a5.jpg', 'Бумага', 150,
         'Moleskine', 'Блокноты', 'Офисные принадлежности'),
        ('Блокнот А4 на пружине', 'photos/notebook_a4.jpg', 'Бумага', 220,
         'Oxford', 'Блокноты', 'Офисные принадлежности'),
        ('Тетрадь 48 листов', 'photos/copybook_48.jpg', 'Бумага', 60,
         'Hatber', 'Тетради', 'Для школьников'),
        ('Тетрадь 96 листов', 'photos/copybook_96.jpg', 'Бумага', 90,
         'Brauberg', 'Тетради', 'Для школьников'),
        ('Ластик мягкий', 'photos/eraser.jpg', 'Резина', 25,
         'Faber-Castell', 'Ластики', 'Для школьников'),
        ('Линейка 30 см', 'photos/ruler.jpg', 'Пластик', 40,
         'Стамм', 'Линейки', 'Для школьников'),
        ('Маркер текстовый жёлтый', 'photos/marker.jpg', 'Пластик', 90,
         'Stabilo', 'Маркеры', 'Офисные принадлежности'),
        ('Папка-скоросшиватель', 'photos/folder.jpg', 'Пластик', 35,
         'Brauberg', 'Папки', 'Офисные принадлежности'),
        ('Набор акварели 18 цветов', 'photos/watercolor.jpg', 'Пластик', 350,
         'Невская палитра', 'Краски', 'Художественные материалы'),
        ('Ножницы офисные 20 см', 'photos/scissors.jpg', 'Металл', 120,
         'Maped', 'Ножницы', 'Офисные принадлежности'),
        ('Клей-карандаш 15 г', 'photos/glue.jpg', 'Пластик', 45,
         'UHU', 'Клей', 'Для школьников'),
        ('Степлер №24', 'photos/stapler.jpg', 'Металл', 180,
         'KW-trio', 'Степлеры', 'Офисные принадлежности'),
        ('Точилка с контейнером', 'photos/sharpener.jpg', 'Металл', 20,
         'Faber-Castell', 'Точилки', 'Для школьников'),
        ('Фломастеры 12 цветов', 'photos/markers_color.jpg', 'Пластик', 200,
         'Crayola', 'Фломастеры', 'Для школьников'),
        ('Пенал тканевый', 'photos/pencilcase.jpg', 'Пластик', 300,
         'Brauberg', 'Пеналы', 'Для школьников'),
        ('Скотч прозрачный 50 м', 'photos/tape.jpg', 'Пластик', 55,
         '3M', 'Скотч', 'Офисные принадлежности'),
        ('Корректор-ручка', 'photos/corrector.jpg', 'Пластик', 65,
         'BIC', 'Корректоры', 'Для школьников'),
        ('Кисть синтетическая №5', 'photos/brush.jpg', 'Дерево', 70,
         'Roubloff', 'Кисти', 'Художественные материалы'),
        ('Масляная пастель 24 цв', 'photos/pastel.jpg', 'Пластик', 400,
         'Сонет', 'Пастель', 'Художественные материалы'),
        ('Бумага А4 500 листов', 'photos/paper_a4.jpg', 'Бумага', 350,
         'SvetoCopy', 'Бумага', 'Офисные принадлежности'),
    ]

    cur.executemany('''
        INSERT INTO products (name, photo, material, price, manufacturer, category, purpose)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # Тестовый пользователь
    cur.execute('''
        INSERT INTO users (fio, email, phone, password)
        VALUES (?, ?, ?, ?)
    ''', ('Иванов Иван Иванович', 'buyer@test.ru', '+79001234567', '1'))

    # Тестовый адрес
    cur.execute('''
        INSERT INTO addresses (user_id, address)
        VALUES (?, ?)
    ''', (1, 'г. Москва, ул. Пушкина, д. 10, кв. 5'))

    conn.commit()
    conn.close()
    print(f'База данных создана: {DB_PATH}')
    print(f'Добавлено товаров: {len(products)}')
    print('Тестовый пользователь: buyer@test.ru / 1')


if __name__ == '__main__':
    create_database()
