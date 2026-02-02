from PIL import Image
import os

# 1. Читаем путь к картинке из txt файла
with open('Новый текстовый документ.txt', 'r') as f:
    image_path = f.read().strip() # .strip() удаляет лишние пробелы/переносы

# 2. Открываем и показываем картинку
if os.path.exists(image_path):
    img = Image.open(image_path)
    img.show()
else:
    print("Файл изображения не найден по указанному пути")


