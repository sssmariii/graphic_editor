from api.editor_api import create_project, add_layer, get_layers, get_preview

if __name__ == "__main__":
    print("Запуск графического редактора (бэкенд)")
    
    # Тест API
    result = create_project()
    print(f"Создан проект: {result}")
    
    add_layer("Фон")
    add_layer("Изображение")
    
    layers = get_layers()
    print(f"Слои: {layers}")
    
    preview = get_preview()
    print(f"Превью: {preview}")
    
    print("Бэкенд работает! Фронтендер может подключаться к API.")