"""Скрипт инициализации БД магазина мебели."""
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

        CREATE TABLE IF NOT EXISTS Materials (
            MaterialID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            CategoryID INTEGER NOT NULL,
            Description TEXT,
            ManufacturerID INTEGER NOT NULL,
            MaterialID INTEGER NOT NULL,
            Price REAL NOT NULL CHECK(Price >= 0),
            Dimensions TEXT,
            StockQuantity INTEGER NOT NULL DEFAULT 0 CHECK(StockQuantity >= 0),
            Discount INTEGER NOT NULL DEFAULT 0 CHECK(Discount >= 0 AND Discount <= 100),
            ImagePath TEXT,
            FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
            FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
            FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID)
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

    cur.executemany(
        'INSERT OR IGNORE INTO Categories (CategoryID, Name) VALUES (?, ?)',
        [
            (1, 'Диваны и кресла'),
            (2, 'Столы и стулья'),
            (3, 'Шкафы и комоды'),
            (4, 'Кровати и матрасы'),
            (5, 'Тумбы и полки'),
        ]
    )

    cur.executemany(
        'INSERT OR IGNORE INTO Manufacturers (ManufacturerID, Name) '
        'VALUES (?, ?)',
        [
            (1, 'Hoff'),
            (2, 'IKEA'),
            (3, 'Askona'),
            (4, 'Шатура'),
            (5, 'Столплит'),
        ]
    )

    cur.executemany(
        'INSERT OR IGNORE INTO Materials (MaterialID, Name) VALUES (?, ?)',
        [
            (1, 'Массив дуба'),
            (2, 'ЛДСП'),
            (3, 'Металл + ткань'),
            (4, 'Экокожа'),
            (5, 'Массив сосны'),
        ]
    )

    cur.executemany(
        'INSERT OR IGNORE INTO Products '
        '(ProductID, Name, CategoryID, Description, ManufacturerID, '
        'MaterialID, Price, Dimensions, StockQuantity, Discount, ImagePath) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [
            (1, 'Диван «Мадрид» угловой', 1,
             'Угловой, раскладной, с ящиком', 1, 3,
             45990, '240×150×85 см', 8, 12, 'images/madrid_sofa.jpg'),
            (2, 'Кровать двуспальная «Сканди»', 4,
             'С подъёмным механизмом, ортопед. основа', 3, 1,
             34990, '160×200 см', 0, 18, 'images/scandi_bed.jpg'),
            (3, 'Стол обеденный «Лофт»', 2,
             'Металл + массив дуба, 6 персон', 5, 1,
             18990, '180×90 см', 14, 5, 'images/loft_table.jpg'),
            (4, 'Шкаф-купе 3-дверный', 3,
             'Зеркало + ЛДСП, 2 штанги', 4, 2,
             28990, '240×60×220 см', 5, 0, 'images/wardrobe.jpg'),
            (5, 'Кресло-качалка «Relax»', 1,
             'Ткань, деревянные полозья', 2, 5,
             12990, '70×90×100 см', 22, 15, 'images/rocking_chair.jpg'),
            (6, 'Комод с 5 ящиками', 3,
             'ЛДСП, цвет белый', 2, 2,
             9990, '80×40×100 см', 31, 8, 'images/chest.jpg'),
        ]
    )

    cur.executemany(
        'INSERT OR IGNORE INTO Orders '
        '(OrderID, UserID, Status, DeliveryAddress, OrderDate, IssueDate) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        [
            (1, 1, 'Новый',
             'Москва, ул. Профсоюзная, д. 12',
             '2026-02-25', None),
            (2, 2, 'Выдан',
             'СПб, Московский пр., д. 78',
             '2026-02-10', '2026-02-18'),
            (3, 1, 'В обработке',
             'Москва, Ленинский пр., д. 45',
             '2026-03-01', None),
        ]
    )

    cur.executemany(
        'INSERT OR IGNORE INTO OrderItems '
        '(ItemID, OrderID, ProductID, Quantity) VALUES (?, ?, ?, ?)',
        [
            (1, 1, 1, 1),
            (2, 1, 5, 2),
            (3, 2, 3, 1),
            (4, 2, 4, 1),
            (5, 3, 2, 1),
        ]
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
    print('База данных создана и заполнена.')
