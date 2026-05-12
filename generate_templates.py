import os
from PIL import Image, ImageDraw, ImageFont


# Список названий шаблонов
names = [
    "Презентация", "Пост для соцсетей", "Открытка", "Визитка",
    "Плакат", "Обложка", "Баннер", "Листовка", "Сертификат", "Приглашение"
]

# Цвета для фона (разные)
colors = [
    (255, 200, 200), (200, 255, 200), (200, 200, 255),
    (255, 255, 200), (255, 200, 255), (200, 255, 255),
    (255, 220, 180), (220, 180, 255), (180, 255, 220), (255, 180, 220)
]


try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)  # для macOS
except:
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # для Windows
    except:
        font = ImageFont.load_default()

for i, (name, bg_color) in enumerate(zip(names, colors), start=1):
    img = Image.new('RGB', (800, 600), bg_color)
    draw = ImageDraw.Draw(img)
    # Рисуем рамку
    draw.rectangle((10, 10, 790, 590), outline=(0,0,0), width=5)
    # Пишем текст
    text = name
    draw.text((400, 300), text, fill=(0,0,0), font=font, anchor="mm")
    filename = f"templates/template{i}.png"
    img.save(filename)
    print(f"Создан {filename}")

print("Готово! 10 шаблонов созданы в папке templates")