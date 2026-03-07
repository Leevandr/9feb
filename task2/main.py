"""
МебельДом — Система управления продажей мебели.
Точка входа приложения.
"""
import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# Тёплая цветовая схема (коричневый/бежевый)
APP_STYLE = """
QWidget {
    font-family: 'Georgia', 'Segoe UI', serif;
    font-size: 13px;
    color: #3E2723;
}
QLineEdit {
    padding: 7px 12px;
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #FFFDF9;
}
QLineEdit:focus {
    border: 2px solid #8D6E63;
}
QComboBox {
    padding: 7px 12px;
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #FFFDF9;
}
QSpinBox, QDoubleSpinBox {
    padding: 7px 10px;
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #FFFDF9;
}
QPushButton {
    padding: 7px 16px;
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #EFEBE9;
    color: #4E342E;
}
QPushButton:hover {
    background: #D7CCC8;
    border-color: #A1887F;
}
#login_btn {
    background: #6D4C41;
    color: white;
    border: none;
    font-weight: bold;
    padding: 9px 22px;
}
#login_btn:hover {
    background: #5D4037;
}
#guest_btn {
    background: #EFEBE9;
    color: #5D4037;
    font-weight: bold;
    padding: 9px 22px;
}
#guest_btn:hover {
    background: #D7CCC8;
}
#add_btn, #add_product_btn {
    background: #558B2F;
    color: white;
    border: none;
    font-weight: bold;
}
#add_btn:hover, #add_product_btn:hover {
    background: #689F38;
}
QTextEdit {
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #FFFDF9;
}
QDateEdit {
    padding: 7px 10px;
    border: 1px solid #BCAAA4;
    border-radius: 8px;
    background: #FFFDF9;
}
QScrollArea {
    background: #FAF3E8;
}
"""


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from init_db import create_database
        create_database()

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    icon_path = os.path.join(BASE_DIR, 'resources', 'logo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    from ui.login_window import LoginWindow
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
