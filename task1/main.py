"""
TechShop — Система управления продажей компьютерной техники.
Точка входа приложения.
"""
import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# Глобальные стили приложения
APP_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 13px;
}
QLineEdit {
    padding: 6px 10px;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
}
QLineEdit:focus {
    border: 2px solid #3498DB;
}
QComboBox {
    padding: 6px 10px;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
}
QSpinBox, QDoubleSpinBox {
    padding: 6px 8px;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
}
QPushButton {
    padding: 6px 14px;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
    color: #2C3E50;
}
QPushButton:hover {
    background: #F0F3F4;
    border-color: #BDC3C7;
}
#login_btn {
    background: #3498DB;
    color: white;
    border: none;
    font-weight: bold;
    padding: 8px 20px;
}
#login_btn:hover {
    background: #2E86C1;
}
#guest_btn {
    background: #ECF0F1;
    color: #2C3E50;
    font-weight: bold;
    padding: 8px 20px;
}
#guest_btn:hover {
    background: #D5DBDB;
}
#add_btn {
    background: #27AE60;
    color: white;
    border: none;
    font-weight: bold;
}
#add_btn:hover {
    background: #2ECC71;
}
QTextEdit {
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
}
QDateEdit {
    padding: 6px 8px;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    background: white;
}
QScrollArea {
    background: #F4F6F7;
}
"""


if __name__ == '__main__':
    # Инициализация БД при первом запуске
    if not os.path.exists(DB_PATH):
        from init_db import create_database, generate_placeholder_image, generate_logo
        create_database()
        generate_placeholder_image()
        generate_logo()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    # Иконка приложения
    icon_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from ui.login_window import LoginWindow
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
