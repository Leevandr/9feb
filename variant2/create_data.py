import os
import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

wb = openpyxl.Workbook()
ws = wb.active
ws.append(['Наименование', 'Артикул', 'Категория', 'Цена', 'Описание', 'Фото'])
ws.append(['iPhone 15', 'A001', 'Смартфоны', 89990, 'Смартфон Apple', 'photos/iphone.jpg'])
ws.append(['Samsung S24', 'A002', 'Смартфоны', 79990, 'Смартфон Samsung', 'photos/samsung.jpg'])
ws.append(['MacBook Air', 'B001', 'Ноутбуки', 129990, 'Ноутбук Apple', 'photos/macbook.jpg'])
ws.append(['Lenovo IdeaPad', 'B002', 'Ноутбуки', 54990, 'Ноутбук Lenovo', 'photos/lenovo.jpg'])
ws.append(['LG OLED 55', 'C001', 'Телевизоры', 99990, 'Телевизор LG', 'photos/lg.jpg'])
ws.append(['Samsung TV 50', 'C002', 'Телевизоры', 44990, 'Телевизор Samsung', 'photos/tv.jpg'])

path = os.path.join(BASE_DIR, 'products.xlsx')
wb.save(path)
print(f'products.xlsx создан: {path}')
