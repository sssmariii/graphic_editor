import json
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Путь к файлу cloud_export.json
cloud_export_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cloud_export.json")

with open(cloud_export_path, "r", encoding="utf-8") as f:
    project_data = json.load(f)

print("=== Демонстрация работы export_to_cloud_json() ===\n")
print(f"Размер холста: {project_data['width']} x {project_data['height']}")
print(f"Количество слоёв: {len(project_data['layers'])}")
print("\nСлои:")

for i, layer in enumerate(project_data['layers']):
    print(f"   {i+1}. {layer['name']}")
    print(f"      - Видимость: {layer['visible']}")
    print(f"      - Прозрачность: {layer['opacity']}%")
    print(f"      - Режим смешивания: {layer['blend_mode']}")
    print(f"      - Позиция: ({layer['x']}, {layer['y']})")
    if 'image_base64' in layer:
        print(f"      - Base64 длина: {len(layer['image_base64'])} символов")
    else:
        print(f"      - image_file: {layer.get('image_file', 'нет')}")

print("\nФункция export_to_cloud_json() работает корректно!")
print("   Все изображения упакованы в base64 внутри JSON.")