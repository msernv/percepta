import os
from PIL import Image, ImageDraw, ImageFont

# Создаем папку для иконок
os.makedirs('static/icons', exist_ok=True)

# Размеры иконок
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    # Создаем изображение с фиолетовым фоном
    img = Image.new('RGB', (size, size), color='#6f42c1')
    d = ImageDraw.Draw(img)
    
    # Пытаемся загрузить шрифт, если нет — используем стандартный
    try:
        font = ImageFont.truetype('arial.ttf', size//2)
    except:
        font = ImageFont.load_default()
    
    # Рисуем букву "P" по центру
    d.text((size//3, size//3), 'P', fill='white', font=font)
    
    # Сохраняем
    img.save(f'static/icons/icon-{size}x{size}.png')
    print(f'✅ Создана иконка {size}x{size}')

print('🎉 Все иконки созданы!')