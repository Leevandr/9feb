import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def authenticate(login, password):
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM Users WHERE Login = ? AND Password = ?',
        (login, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def load_products():
    conn = get_connection()
    rows = conn.execute('''
        SELECT p.*, c.Name AS CategoryName,
               m.Name AS ManufacturerName, s.Name AS SupplierName
        FROM Products p
        JOIN Categories c ON p.CategoryID = c.CategoryID
        JOIN Manufacturers m ON p.ManufacturerID = m.ManufacturerID
        JOIN Suppliers s ON p.SupplierID = s.SupplierID
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(product_id):
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM Products WHERE ProductID = ?',
        (product_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(data):
    conn = get_connection()
    conn.execute('''
        INSERT INTO Products
            (Name, CategoryID, Description, ManufacturerID, SupplierID,
             Price, Unit, StockQuantity, Discount, ImagePath)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['Name'], data['CategoryID'], data['Description'],
        data['ManufacturerID'], data['SupplierID'], data['Price'],
        data['Unit'], data['StockQuantity'], data['Discount'],
        data['ImagePath']
    ))
    conn.commit()
    conn.close()


def update_product(product_id, data):
    conn = get_connection()
    conn.execute('''
        UPDATE Products SET
            Name = ?, CategoryID = ?, Description = ?,
            ManufacturerID = ?, SupplierID = ?, Price = ?,
            Unit = ?, StockQuantity = ?, Discount = ?, ImagePath = ?
        WHERE ProductID = ?
    ''', (
        data['Name'], data['CategoryID'], data['Description'],
        data['ManufacturerID'], data['SupplierID'], data['Price'],
        data['Unit'], data['StockQuantity'], data['Discount'],
        data['ImagePath'], product_id
    ))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    in_order = conn.execute(
        'SELECT COUNT(*) FROM OrderItems WHERE ProductID = ?',
        (product_id,)
    ).fetchone()[0]
    if in_order > 0:
        conn.close()
        return False
    conn.execute(
        'DELETE FROM Products WHERE ProductID = ?', (product_id,))
    conn.commit()
    conn.close()
    return True


def product_in_orders(product_id):
    conn = get_connection()
    count = conn.execute(
        'SELECT COUNT(*) FROM OrderItems WHERE ProductID = ?',
        (product_id,)
    ).fetchone()[0]
    conn.close()
    return count > 0


def load_categories():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Categories ORDER BY Name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_manufacturers():
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM Manufacturers ORDER BY Name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_suppliers():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM Suppliers ORDER BY Name').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_orders():
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM Orders ORDER BY OrderID DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_by_id(order_id):
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM Orders WHERE OrderID = ?', (order_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_order(data):
    conn = get_connection()
    conn.execute('''
        INSERT INTO Orders (UserID, Status, DeliveryAddress,
                            OrderDate, IssueDate)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['UserID'], data['Status'], data['DeliveryAddress'],
        data['OrderDate'], data['IssueDate']
    ))
    conn.commit()
    conn.close()


def update_order(order_id, data):
    conn = get_connection()
    conn.execute('''
        UPDATE Orders SET
            Status = ?, DeliveryAddress = ?,
            OrderDate = ?, IssueDate = ?
        WHERE OrderID = ?
    ''', (
        data['Status'], data['DeliveryAddress'],
        data['OrderDate'], data['IssueDate'], order_id
    ))
    conn.commit()
    conn.close()


def delete_order(order_id):
    conn = get_connection()
    conn.execute(
        'DELETE FROM OrderItems WHERE OrderID = ?', (order_id,))
    conn.execute(
        'DELETE FROM Orders WHERE OrderID = ?', (order_id,))
    conn.commit()
    conn.close()
