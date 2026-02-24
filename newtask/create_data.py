"""
Скрипт инициализации базы данных аптеки.
Создаёт SQLite-базу pharmacy.db с таблицами, тестовыми данными
и генерирует изображения-заглушки для препаратов.
"""
import os
import sqlite3
import struct
import zlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pharmacy.db')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')


def create_medicine_png(width, height, r, g, b):
    """Создаёт PNG — цветной фон с белым медицинским крестом."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return (struct.pack('>I', len(data)) + c +
                struct.pack('>I', zlib.crc32(c) & 0xffffffff))

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)

    cx, cy = width // 2, height // 2
    arm_w = width // 6
    arm_h = height // 3

    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            in_cross = False
            if cx - arm_w <= x <= cx + arm_w and cy - arm_h <= y <= cy + arm_h:
                in_cross = True
            if cy - arm_w <= y <= cy + arm_w and cx - arm_h <= x <= cx + arm_h:
                in_cross = True

            if x < 3 or x >= width - 3 or y < 3 or y >= height - 3:
                raw += struct.pack('BBB',
                                   max(r - 50, 0), max(g - 50, 0), max(b - 50, 0))
            elif in_cross:
                raw += struct.pack('BBB', 255, 255, 255)
            else:
                raw += struct.pack('BBB', r, g, b)

    idat = zlib.compress(raw)
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')


def generate_photos(products_data):
    """Генерирует фото-заглушки для каждого препарата."""
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    colors = {
        'Сердечно-сосудистые': (220, 80, 80),
        'Обезболивающие': (80, 140, 220),
        'Антибиотики': (220, 180, 60),
        'ЛОР': (100, 200, 180),
        'ЖКТ': (180, 120, 200),
        'Антигистаминные': (200, 160, 100),
        'Ранозаживляющие': (120, 200, 120),
        'Витамины': (240, 200, 80),
        'Седативные': (160, 180, 220),
        'От кашля': (180, 200, 140),
        'Уход за кожей': (240, 180, 200),
        'Антисептики': (100, 180, 220),
        'Медизделия': (200, 200, 200),
    }

    for product in products_data:
        photo_name = product[1]
        disease = product[6]
        color = colors.get(disease, (180, 180, 180))

        path = os.path.join(BASE_DIR, photo_name)
        if not os.path.exists(path):
            png_data = create_medicine_png(64, 64, *color)
            with open(path, 'wb') as f:
                f.write(png_data)


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------- Таблица препаратов ----------
    cur.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo TEXT DEFAULT '',
            instruction TEXT DEFAULT '',
            release_form TEXT DEFAULT '',
            price REAL DEFAULT 0,
            manufacturer TEXT DEFAULT '',
            disease_group TEXT DEFAULT '',
            prescription TEXT DEFAULT '',
            active_ingredient TEXT DEFAULT ''
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
    # (name, photo, instruction, release_form, price,
    #  manufacturer, disease_group, prescription, active_ingredient)
    products = [
        ('Аспирин', 'photos/aspirin.png',
         'По 1 таблетке после еды',
         'Таблетки', 120, 'Bayer (Импортный)',
         'Сердечно-сосудистые', 'Безрецептурный',
         'Ацетилсалициловая кислота'),

        ('Парацетамол', 'photos/paracetamol.png',
         'По 1-2 табл. до 4 раз/сутки',
         'Таблетки', 45, 'Фармстандарт (Отечественный)',
         'Обезболивающие', 'Безрецептурный',
         'Парацетамол'),

        ('Амоксициллин', 'photos/amoxicillin.png',
         'По 500 мг 3 раза/сутки, курс 7 дней',
         'Капсулы', 180, 'АВВА РУС (Отечественный)',
         'Антибиотики', 'Рецептурный',
         'Амоксициллин'),

        ('Ибупрофен', 'photos/ibuprofen.png',
         'По 200-400 мг до 3 раз/сутки после еды',
         'Таблетки', 95, 'Синтез (Отечественный)',
         'Обезболивающие', 'Безрецептурный',
         'Ибупрофен'),

        ('Нафтизин', 'photos/naphthyzin.png',
         'По 1-3 капли в нос 3 раза/сутки',
         'Капли', 35, 'Славянская аптека (Отечественный)',
         'ЛОР', 'Безрецептурный',
         'Нафазолин'),

        ('Мезим форте', 'photos/mezim.png',
         'По 1-2 табл. во время еды',
         'Таблетки', 280, 'Berlin-Chemie (Импортный)',
         'ЖКТ', 'Безрецептурный',
         'Панкреатин'),

        ('Лоратадин', 'photos/loratadin.png',
         'По 1 табл. 1 раз/сутки',
         'Таблетки', 60, 'Вертекс (Отечественный)',
         'Антигистаминные', 'Безрецептурный',
         'Лоратадин'),

        ('Левомеколь', 'photos/levomekol.png',
         'Наносить на рану 1-2 раза/сутки',
         'Мазь', 130, 'Нижфарм (Отечественный)',
         'Ранозаживляющие', 'Безрецептурный',
         'Хлорамфеникол + Метилурацил'),

        ('Витамин С 1000 мг', 'photos/vitamin_c.png',
         '1 шипучую табл. в стакане воды 1 раз/сутки',
         'Шипучие таблетки', 350, 'Bayer (Импортный)',
         'Витамины', 'Безрецептурный',
         'Аскорбиновая кислота'),

        ('Валерианы экстракт', 'photos/valerian.png',
         'По 1-2 табл. 3 раза/сутки',
         'Таблетки', 75, 'Фармстандарт (Отечественный)',
         'Седативные', 'Безрецептурный',
         'Валерианы экстракт'),

        ('Називин', 'photos/nazivin.png',
         'По 1 впрыскиванию в нос 2-3 раза/сутки',
         'Спрей', 190, 'Merck (Импортный)',
         'ЛОР', 'Безрецептурный',
         'Оксиметазолин'),

        ('Омепразол', 'photos/omeprazol.png',
         'По 1 капсуле утром натощак',
         'Капсулы', 85, 'Озон (Отечественный)',
         'ЖКТ', 'Безрецептурный',
         'Омепразол'),

        ('Диклофенак', 'photos/diclofenac.png',
         'Тонким слоем на больной участок 3-4 раза/сутки',
         'Гель', 150, 'Хемофарм (Импортный)',
         'Обезболивающие', 'Безрецептурный',
         'Диклофенак натрия'),

        ('Амброксол', 'photos/ambroxol.png',
         'По 10 мл сиропа 3 раза/сутки',
         'Сироп', 120, 'Фармстандарт (Отечественный)',
         'От кашля', 'Безрецептурный',
         'Амброксол'),

        ('Цетиризин', 'photos/cetirizin.png',
         'По 1 табл. 1 раз/сутки вечером',
         'Таблетки', 110, 'Др. Редди (Импортный)',
         'Антигистаминные', 'Безрецептурный',
         'Цетиризин'),

        ('Бепантен', 'photos/bepanthen.png',
         'Тонким слоем 1-2 раза/сутки',
         'Крем', 520, 'Bayer (Импортный)',
         'Уход за кожей', 'Безрецептурный',
         'Декспантенол'),

        ('Фурацилин', 'photos/furacilin.png',
         '1 табл. на 100 мл воды для полоскания',
         'Раствор', 55, 'Авексима (Отечественный)',
         'Антисептики', 'Безрецептурный',
         'Нитрофурал'),

        ('Корвалол', 'photos/corvalol.png',
         'По 15-30 капель 2-3 раза/сутки до еды',
         'Капли', 25, 'Фармстандарт (Отечественный)',
         'Сердечно-сосудистые', 'Безрецептурный',
         'Фенобарбитал + Этилбромизовалерианат'),

        ('Мирамистин', 'photos/miramistin.png',
         'Орошать поверхность 3-4 раза/сутки',
         'Раствор', 380, 'Инфамед (Отечественный)',
         'Антисептики', 'Безрецептурный',
         'Бензилдиметил'),

        ('Смекта', 'photos/smecta.png',
         '1 пакетик на 50 мл воды, 3 раза/сутки',
         'Порошок', 160, 'Ipsen (Импортный)',
         'ЖКТ', 'Безрецептурный',
         'Смектит диоктаэдрический'),

        ('Анальгин', 'photos/analgin.png',
         'По 1 табл. 2-3 раза/сутки после еды',
         'Таблетки', 30, 'Фармстандарт (Отечественный)',
         'Обезболивающие', 'Безрецептурный',
         'Метамизол натрия'),

        ('Супрастин', 'photos/suprastin.png',
         'По 1 табл. 3-4 раза/сутки во время еды',
         'Таблетки', 140, 'Egis (Импортный)',
         'Антигистаминные', 'Рецептурный',
         'Хлоропирамин'),

        ('Нурофен', 'photos/nurofen.png',
         'По 5-10 мл суспензии 3 раза/сутки',
         'Сироп', 250, 'Reckitt Benckiser (Импортный)',
         'Обезболивающие', 'Безрецептурный',
         'Ибупрофен'),

        ('Пластырь бактерицидный', 'photos/plaster.png',
         'Наклеить на чистую сухую кожу',
         'Пластырь', 65, 'Мастер Юни (Отечественный)',
         'Медизделия', 'Безрецептурный',
         '—'),

        ('Бинт медицинский', 'photos/bandage.png',
         'Для перевязки ран и фиксации повязок',
         'Медизделие', 40, 'Клинса (Отечественный)',
         'Медизделия', 'Безрецептурный',
         '—'),
    ]

    cur.executemany('''
        INSERT INTO products
            (name, photo, instruction, release_form, price,
             manufacturer, disease_group, prescription, active_ingredient)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # Генерация фото-заглушек
    generate_photos(products)

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
    print(f'Добавлено препаратов: {len(products)}')
    print('Тестовый пользователь: buyer@test.ru / 1')


if __name__ == '__main__':
    create_database()
