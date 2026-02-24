"""
Скрипт инициализации базы данных аптеки.
Создаёт SQLite-базу pharmacy.db с таблицами, тестовыми данными
и генерирует изображения упаковок через Pillow.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'pharmacy.db')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')

# Цвета по группам заболеваний: (accent_hex, pastel_hex)
COLORS = {
    'Сердечно-сосудистые': ('#E74C3C', '#FADBD8'),
    'Обезболивающие': ('#3498DB', '#D6EAF8'),
    'Антибиотики': ('#E67E22', '#FDEBD0'),
    'ЛОР': ('#1ABC9C', '#D1F2EB'),
    'ЖКТ': ('#9B59B6', '#E8DAEF'),
    'Антигистаминные': ('#F39C12', '#FEF9E7'),
    'Ранозаживляющие': ('#27AE60', '#D5F5E3'),
    'Витамины': ('#F1C40F', '#FEF5D4'),
    'Уход за кожей': ('#E91E8C', '#FDE'),
    'Антисептики': ('#2E86C1', '#D4E6F1'),
}

FONT_PATHS = [
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/HelveticaNeue.ttc',
    '/System/Library/Fonts/ArialHB.ttc',
    '/System/Library/Fonts/Geneva.ttf',
    '/System/Library/Fonts/LucidaGrande.ttc',
]


def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def generate_photos(products_data):
    """Генерирует изображения упаковок лекарств через Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('Pillow не установлен, изображения не созданы')
        return

    os.makedirs(PHOTOS_DIR, exist_ok=True)

    # Ищем шрифт с поддержкой кириллицы
    font_path = None
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            font_path = fp
            break

    def get_font(size):
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    for product in products_data:
        filename = product[1].replace('photos/', '')
        name = product[0]
        form = product[3]
        disease = product[6]

        accent = hex_to_rgb(COLORS.get(disease, ('#888', '#EEE'))[0])
        darker = tuple(max(0, c - 50) for c in accent)

        w, h = 250, 250
        img = Image.new('RGB', (w, h), (248, 249, 252))
        draw = ImageDraw.Draw(img)

        # Тень коробки
        draw.rounded_rectangle(
            [20, 20, w - 10, h - 48], radius=16,
            fill=(215, 218, 225))

        # Коробка лекарства
        draw.rounded_rectangle(
            [15, 15, w - 15, h - 52], radius=16, fill=accent)

        # Белая этикетка
        draw.rounded_rectangle(
            [30, 55, w - 30, h - 72], radius=10, fill='white')

        # Медицинский крест (белый, левый верхний угол коробки)
        cx_c, cy_c = 38, 35
        draw.rectangle(
            [cx_c - 3, cy_c - 10, cx_c + 3, cy_c + 10], fill='white')
        draw.rectangle(
            [cx_c - 10, cy_c - 3, cx_c + 10, cy_c + 3], fill='white')

        # Иконка формы (правый верхний угол, цветной кружок)
        badge_x, badge_y = w - 50, 35
        draw.ellipse(
            [badge_x - 14, badge_y - 14, badge_x + 14, badge_y + 14],
            fill='white')

        # Простая иконка формы внутри кружка
        if form in ('Таблетки', 'Шипучие таблетки'):
            # Таблетка (овал с линией)
            draw.ellipse(
                [badge_x - 9, badge_y - 5, badge_x + 9, badge_y + 5],
                fill=accent)
            draw.line(
                [(badge_x, badge_y - 5), (badge_x, badge_y + 5)],
                fill='white', width=1)
        elif form == 'Капсулы':
            draw.rounded_rectangle(
                [badge_x - 10, badge_y - 4, badge_x + 10, badge_y + 4],
                radius=4, fill=accent)
            draw.rectangle(
                [badge_x, badge_y - 4, badge_x + 10, badge_y + 4],
                fill=darker)
        elif form in ('Капли', 'Спрей', 'Сироп', 'Раствор'):
            # Бутылочка
            draw.rectangle(
                [badge_x - 5, badge_y - 2, badge_x + 5, badge_y + 10],
                fill=accent)
            draw.rectangle(
                [badge_x - 2, badge_y - 8, badge_x + 2, badge_y - 2],
                fill=accent)
        elif form in ('Мазь', 'Гель', 'Крем'):
            # Тюбик
            draw.rectangle(
                [badge_x - 8, badge_y - 3, badge_x + 5, badge_y + 3],
                fill=accent)
            draw.polygon(
                [(badge_x + 5, badge_y - 2),
                 (badge_x + 10, badge_y),
                 (badge_x + 5, badge_y + 2)],
                fill=darker)
        else:
            draw.rectangle(
                [badge_x - 2, badge_y - 7, badge_x + 2, badge_y + 7],
                fill=accent)
            draw.rectangle(
                [badge_x - 7, badge_y - 2, badge_x + 7, badge_y + 2],
                fill=accent)

        # Название на этикетке
        font_name = get_font(17)
        display = name if len(name) <= 15 else name[:14] + '.'
        bbox = draw.textbbox((0, 0), display, font=font_name)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((w - tw) // 2, 65), display,
            fill=darker, font=font_name)

        # Форма выпуска на этикетке
        font_form = get_font(12)
        bbox2 = draw.textbbox((0, 0), form, font=font_form)
        tw2 = bbox2[2] - bbox2[0]
        draw.text(
            ((w - tw2) // 2, 92), form,
            fill=(130, 130, 130), font=font_form)

        # Инструкция (мелким шрифтом на этикетке)
        instruction = product[2]
        font_instr = get_font(9)
        short_instr = instruction if len(instruction) <= 35 \
            else instruction[:34] + '.'
        bbox3 = draw.textbbox((0, 0), short_instr, font=font_instr)
        tw3 = bbox3[2] - bbox3[0]
        draw.text(
            ((w - tw3) // 2, 115), short_instr,
            fill=(160, 160, 160), font=font_instr)

        # Группа заболеваний (под коробкой)
        font_group = get_font(11)
        draw.text((15, h - 40), disease, fill=(140, 140, 145), font=font_group)

        # Цена (справа под коробкой)
        price_text = f'{product[4]:.0f} руб'
        font_price = get_font(13)
        bbox4 = draw.textbbox((0, 0), price_text, font=font_price)
        tw4 = bbox4[2] - bbox4[0]
        draw.text(
            (w - tw4 - 15, h - 40), price_text,
            fill=accent, font=font_price)

        path = os.path.join(PHOTOS_DIR, filename)
        img.save(path, 'PNG')

    print(f'Создано {len(products_data)} изображений в {PHOTOS_DIR}')


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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

    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT DEFAULT '',
            password TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_method TEXT DEFAULT '',
            delivery_address TEXT DEFAULT '',
            total REAL DEFAULT 0,
            status TEXT DEFAULT '',
            order_date TEXT DEFAULT '',
            delivery_date TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

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

    # 12 препаратов (фото только у тех, для которых есть реальные изображения)
    products = [
        ('Аспирин', 'photos/аспирин.png',
         'По 1 таблетке после еды',
         'Таблетки', 120, 'Bayer (Импортный)',
         'Сердечно-сосудистые', 'Безрецептурный',
         'Ацетилсалициловая кислота'),

        ('Парацетамол', '',
         'По 1-2 табл. до 4 раз/сутки',
         'Таблетки', 45, 'Фармстандарт (Отечественный)',
         'Обезболивающие', 'Безрецептурный',
         'Парацетамол'),

        ('Амоксициллин', '',
         'По 500 мг 3 раза/сутки, 7 дней',
         'Капсулы', 180, 'АВВА РУС (Отечественный)',
         'Антибиотики', 'Рецептурный',
         'Амоксициллин'),

        ('Нафтизин', '',
         'По 1-3 капли в нос 3 раза/сутки',
         'Капли', 35, 'Славянская аптека (Отечественный)',
         'ЛОР', 'Безрецептурный',
         'Нафазолин'),

        ('Мезим форте', 'photos/mezzm.png',
         'По 1-2 табл. во время еды',
         'Таблетки', 280, 'Berlin-Chemie (Импортный)',
         'ЖКТ', 'Безрецептурный',
         'Панкреатин'),

        ('Лоратадин', '',
         'По 1 табл. 1 раз/сутки',
         'Таблетки', 60, 'Вертекс (Отечественный)',
         'Антигистаминные', 'Безрецептурный',
         'Лоратадин'),

        ('Левомеколь', '',
         'Наносить на рану 1-2 раза/сутки',
         'Мазь', 130, 'Нижфарм (Отечественный)',
         'Ранозаживляющие', 'Безрецептурный',
         'Хлорамфеникол + Метилурацил'),

        ('Витамин С', 'photos/витаминц.png',
         '1 табл. в стакане воды 1 раз/сутки',
         'Шипучие таблетки', 350, 'Bayer (Импортный)',
         'Витамины', 'Безрецептурный',
         'Аскорбиновая кислота'),

        ('Називин', '',
         'По 1 впрыскиванию 2-3 раза/сутки',
         'Спрей', 190, 'Merck (Импортный)',
         'ЛОР', 'Безрецептурный',
         'Оксиметазолин'),

        ('Бепантен', '',
         'Тонким слоем 1-2 раза/сутки',
         'Крем', 520, 'Bayer (Импортный)',
         'Уход за кожей', 'Безрецептурный',
         'Декспантенол'),

        ('Мирамистин', '',
         'Орошать 3-4 раза/сутки',
         'Раствор', 380, 'Инфамед (Отечественный)',
         'Антисептики', 'Безрецептурный',
         'Бензилдиметил'),

        ('Нурофен', '',
         'По 5-10 мл 3 раза/сутки',
         'Сироп', 250, 'Reckitt Benckiser (Импортный)',
         'Обезболивающие', 'Безрецептурный',
         'Ибупрофен'),
    ]

    cur.executemany('''
        INSERT INTO products
            (name, photo, instruction, release_form, price,
             manufacturer, disease_group, prescription, active_ingredient)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    cur.execute('''
        INSERT INTO users (fio, email, phone, password)
        VALUES (?, ?, ?, ?)
    ''', ('Иванов Иван Иванович', 'buyer@test.ru', '+79001234567', '1'))

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
