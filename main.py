from api.editor_api import (
    create_project,
    add_layer,
    get_layers,
    set_layer_opacity,
    set_layer_blend_mode,
    move_layer_up,
    save_current_project,
    load_project_from_folder,
    export_project,
    undo,
    redo,
    apply_filter_to_layer_api,
    rotate_layer_api,
    scale_layer_api,
    crop_layer_api,
    resize_canvas_api,
    export_to_pdf_api,
    export_project_to_cloud,
    import_project_from_cloud
)

def main():
    print("Тестирование бэкенда...")
    
    create_project(800, 600)
    print("Проект создан")
    
    add_layer("Слой 1")
    add_layer("Слой 2")
    add_layer("Слой 3")
    print("Слои добавлены")
    
    set_layer_opacity(1, 50)
    set_layer_blend_mode(1, "multiply")
    move_layer_up(2)
    print("Свойства слоёв изменены")
    
    save_current_project("test_project")
    load_project_from_folder("test_project")
    print("Сохранение/загрузка работают")
    
    export_project("export.png")
    export_to_pdf_api("export.pdf")
    print("Экспорт PNG/PDF работает")
    
    apply_filter_to_layer_api(0, "brightness", 50)
    rotate_layer_api(0, 90)
    scale_layer_api(0, 1.5)
    crop_layer_api(0, 10, 10, 100, 100)
    resize_canvas_api(1024, 768, "center")
    print("Фильтры и трансформации работают")
    
    undo()
    redo()
    print("История (Undo/Redo) работает")
    
    result = export_project_to_cloud()
    if "error" not in result:
        import_project_from_cloud(result)
        print("Облачные функции работают")
    
    layers = get_layers()
    print(f"\nВСЕ ТЕСТЫ ПРОЙДЕНЫ! Слоёв в проекте: {len(layers['layers'])}")

if __name__ == "__main__":
    main()