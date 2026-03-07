"""
Скрипт инициализации базы данных.
Создаёт таблицы и заполняет их начальными данными из Приложения 2.
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL CHECK(Role IN ('client', 'manager', 'admin')),
            FIO TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Categories (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Manufacturers (
            ManufacturerID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            CategoryID INTEGER NOT NULL,
            Description TEXT,
            ManufacturerID INTEGER NOT NULL,
            SupplierID INTEGER NOT NULL,
            Price REAL NOT NULL CHECK(Price >= 0),
            Unit TEXT NOT NULL DEFAULT 'шт',
            StockQuantity INTEGER NOT NULL DEFAULT 0 CHECK(StockQuantity >= 0),
            Discount INTEGER NOT NULL DEFAULT 0 CHECK(Discount >= 0 AND Discount <= 100),
            ImagePath TEXT,
            FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
            FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
            FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
        );

        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Status TEXT NOT NULL,
            DeliveryAddress TEXT NOT NULL,
            OrderDate TEXT NOT NULL,
            IssueDate TEXT,
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        );

        CREATE TABLE IF NOT EXISTS OrderItems (
            ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL DEFAULT 1 CHECK(Quantity > 0),
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        );
    ''')

    # Пользователи
    cur.executemany(
        'INSERT OR IGNORE INTO Users (UserID, Login, Password, Role, FIO) '
        'VALUES (?, ?, ?, ?, ?)',
        [
            (1, 'client1', '123456', 'client', 'Иванов Иван Иванович'),
            (2, 'client2', '654321', 'client', 'Петрова Анна Сергеевна'),
            (3, 'manager', 'manager', 'manager', 'Сидоров Пётр Алексеевич'),
            (4, 'admin', 'admin', 'admin', 'Васильева Ольга Дмитриевна'),
        ]
    )

    # Категории
    cur.executemany(
        'INSERT OR IGNORE INTO Categories (CategoryID, Name) VALUES (?, ?)',
        [
            (1, 'Смартфоны'),
            (2, 'Ноутбуки'),
            (3, 'Наушники'),
            (4, 'Зарядные устройства'),
        ]
    )

    # Производители
    cur.executemany(
        'INSERT OR IGNORE INTO Manufacturers (ManufacturerID, Name) '
        'VALUES (?, ?)',
        [
            (1, 'Apple'),
            (2, 'Samsung'),
            (3, 'Huawei'),
            (4, 'Sony'),
            (5, 'Lenovo'),
        ]
    )

    # Поставщики
    cur.executemany(
        'INSERT OR IGNORE INTO Suppliers (SupplierID, Name) VALUES (?, ?)',
        [
            (1, 'ООО «ТехОпт»'),
            (2, 'ИП «ГаджетМир»'),
            (3, 'ЗАО «ЭлектроСнаб»'),
            (4, 'ООО «МирТехника»'),
        ]
    )

    # Товары
    cur.executemany(
        'INSERT OR IGNORE INTO Products '
        '(ProductID, Name, CategoryID, Description, ManufacturerID, '
        'SupplierID, Price, Unit, StockQuantity, Discount, ImagePath) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [
            (1, 'iPhone 16 Pro', 1,
             'Флагман 2025 года, 256 ГБ', 1, 1,
             134990, 'шт', 34, 8, 'images/iphone16.jpg'),
            (2, 'Samsung Galaxy S25', 1,
             'Смартфон с отличной камерой 200 МП', 2, 1,
             94990, 'шт', 0, 22, 'images/galaxys25.jpg'),
            (3, 'MacBook Air M3', 2,
             '13", 16 ГБ, 512 ГБ SSD', 1, 2,
             149990, 'шт', 12, 5, 'images/macbookair.jpg'),
            (4, 'Lenovo ThinkPad X1', 2,
             'Бизнес-ноутбук, Intel Core Ultra', 5, 3,
             124990, 'шт', 7, 0, 'images/thinkpad.jpg'),
            (5, 'AirPods Max', 3,
             'Премиум наушники с шумоподавлением', 1, 4,
             54990, 'шт', 28, 12, 'images/airpodsmax.jpg'),
            (6, 'Sony WH-1000XM5', 3,
             'Лучшие беспроводные наушники 2025', 4, 2,
             32990, 'шт', 15, 18, 'images/sonywh.jpg'),
            (7, 'Xiaomi 65W GaN Charger', 4,
             'Быстрая зарядка GaN', 3, 1,
             2490, 'шт', 87, 0, 'images/xiaomi65.jpg'),
        ]
    )

    # Заказы
    cur.executemany(
        'INSERT OR IGNORE INTO Orders '
        '(OrderID, UserID, Status, DeliveryAddress, OrderDate, IssueDate) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        [
            (1, 1, 'Новый',
             'Москва, ул. Тверская, д. 15, кв. 8',
             '2026-03-01', None),
            (2, 2, 'Выдан',
             'СПб, Невский пр., д. 45',
             '2026-02-20', '2026-02-25'),
            (3, 1, 'В обработке',
             'Москва, Ленинградский пр., д. 37',
             '2026-03-02', None),
        ]
    )

    # Состав заказов
    cur.executemany(
        'INSERT OR IGNORE INTO OrderItems '
        '(ItemID, OrderID, ProductID, Quantity) VALUES (?, ?, ?, ?)',
        [
            (1, 1, 1, 1),
            (2, 1, 5, 1),
            (3, 2, 3, 1),
            (4, 3, 2, 1),
            (5, 3, 6, 1),
        ]
    )

    conn.commit()
    conn.close()


def generate_placeholder_image():
    """Создаёт картинку-заглушку picture.png если её нет."""
    path = os.path.join(BASE_DIR, 'resources', 'picture.png')
    if os.path.exists(path):
        return
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
        from PyQt6.QtCore import Qt

        app = QApplication.instance()
        need_app = app is None
        if need_app:
            app = QApplication([])

        pix = QPixmap(300, 200)
        pix.fill(QColor('#E0E0E0'))
        painter = QPainter(pix)
        painter.setPen(QColor('#999999'))
        font = QFont('Arial', 14)
        painter.setFont(font)
        painter.drawText(
            pix.rect(), Qt.AlignmentFlag.AlignCenter, 'Нет фото')
        painter.end()
        pix.save(path)
    except Exception:
        pass


def generate_logo():
    """Создаёт логотип компании если его нет."""
    path = os.path.join(BASE_DIR, 'resources', 'logo.png')
    if os.path.exists(path):
        return
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
        from PyQt6.QtCore import Qt

        app = QApplication.instance()
        need_app = app is None
        if need_app:
            app = QApplication([])

        pix = QPixmap(200, 60)
        pix.fill(QColor('#2C3E50'))
        painter = QPainter(pix)
        painter.setPen(QColor('#FFFFFF'))
        font = QFont('Arial', 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            pix.rect(), Qt.AlignmentFlag.AlignCenter, 'TechShop')
        painter.end()
        pix.save(path)
    except Exception:
        pass


if __name__ == '__main__':
    create_database()
    generate_placeholder_image()
    generate_logo()
    print('База данных создана и заполнена.')
