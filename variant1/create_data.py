import os
import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

wb = openpyxl.Workbook()
ws = wb.active
ws.append(['Название', 'Автор', 'Жанр', 'Фото'])
ws.append(['Война и мир', 'Толстой', 'Роман', 'photos/war.jpg'])
ws.append(['Шерлок Холмс', 'Конан Дойл', 'Детектив', 'photos/sherlock.jpg'])
ws.append(['Дюна', 'Фрэнк Герберт', 'Фантастика', 'photos/dune.jpg'])
ws.append(['Анна Каренина', 'Толстой', 'Роман', 'photos/anna.jpg'])
ws.append(['Убийство в Восточном экспрессе', 'Агата Кристи', 'Детектив', 'photos/orient.jpg'])
ws.append(['Нейромант', 'Уильям Гибсон', 'Фантастика', 'photos/neuro.jpg'])

path = os.path.join(BASE_DIR, 'books.xlsx')
wb.save(path)
print(f'books.xlsx создан: {path}')
