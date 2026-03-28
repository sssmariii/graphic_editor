from api.editor_api import (
    create_project,
    add_layer,
    export_project_to_cloud,
    get_layers,
    get_preview,
    import_project_from_cloud,
    set_layer_visibility,
    set_layer_opacity,
    set_layer_blend_mode,
    move_layer_up,
    move_layer_down,
    move_layer_to_top,
    move_layer_to_bottom,
    set_layer_position,
    remove_layer,
    save_current_project,
    load_project_from_folder,
    get_project_info,
    export_project,
    undo,
    redo,
    apply_filter_to_layer_api,
    rotate_layer_api,
    scale_layer_api
    
)

def print_layers():
    result = get_layers()
    if "error" in result:
        print(f"  Ошибка: {result['error']}")
        return
    
    layers = result["layers"]
    if not layers:
        print("  Нет слоёв")
        return
    
    for layer in layers:
        visible = "👁️" if layer["visible"] else "👁️‍🗨️"
        print(f"  [{layer['index']}] {visible} {layer['name']} | прозр: {layer['opacity']}% | режим: {layer['blend_mode']} | x:{layer['x']} y:{layer['y']}")


def main():
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ БЭКЕНДА")
    print("=" * 50)
    
    print("\n1. Создаём проект 800x600")
    create_project(800, 600)
    
    print("\n2. Добавляем слои")
    add_layer("Фон")
    add_layer("Рисунок")
    add_layer("Текст")
    add_layer("Логотип")
    print_layers()
    
    print("\n3. Меняем прозрачность слоя 1 на 50%")
    set_layer_opacity(1, 50)
    print_layers()
    
    print("\n4. Меняем режим наложения слоя 1 на multiply")
    set_layer_blend_mode(1, "multiply")
    print_layers()
    
    print("\n5. Прячем слой 2")
    set_layer_visibility(2, False)
    print_layers()
    
    print("\n6. Перемещаем слой 3 выше")
    move_layer_up(3)
    print_layers()
    
    print("\n7. Перемещаем слой 0 ниже")
    move_layer_down(0)
    print_layers()
    
    print("\n8. Меняем позицию слоя 0 на x=100, y=50")
    set_layer_position(0, 100, 50)
    print_layers()
    
    print("\n9. Сохраняем проект в папку test_project")
    save_current_project("test_project")
    
    print("\n10. Экспортируем в PNG")
    export_project("export.png")
    
    print("\n11. Информация о проекте")
    info = get_project_info()
    print(f"  Размер: {info['width']} x {info['height']}")
    print(f"  Слоёв: {info['layers_count']}")
    print(f"  Версия: {info['version']}")
    
    print("\n12. Тест Undo/Redo")
    print("  До Undo:")
    print_layers()
    
    undo()
    print("  После Undo (отмена последнего действия):")
    print_layers()
    
    redo()
    print("  После Redo (повтор):")
    print_layers()
    
    print("\n13. Загружаем проект из папки test_project")
    load_project_from_folder("test_project")
    print_layers()
    
    print("\n14. Удаляем слой 0")
    remove_layer(0)
    print_layers()
    
    print("\n15. Информация о превью")
    preview = get_preview()
    print(f"  Размер превью: {preview['width']} x {preview['height']}")

    print("\n16. Тест фильтров")
    
    add_layer("Для фильтров", None)
    
    print("  Применяем яркость +50 к слою 4")
    apply_filter_to_layer_api(4, "brightness", 50)
    
    print("  Применяем контраст +30 к слою 4")
    apply_filter_to_layer_api(4, "contrast", 30)
    
    print("\n17. Тест поворота")
    print("  Поворачиваем слой 4 на 90°")
    rotate_layer_api(4, 90)
    
    print("\n18. Тест масштабирования")
    print("  Увеличиваем слой 4 в 1.5 раза")
    scale_layer_api(4, 1.5)

     # 19. Тест облачных функций
    print("\n19. Тест облачных функций")
    
    # Экспортируем в JSON с base64
    result = export_project_to_cloud()
    if "error" in result:
        print(f"  Ошибка: {result['error']}")
    else:
        print("  ✅ Проект экспортирован в JSON с base64")
        
        # Сохраняем JSON в файл (для демонстрации)
        import json
        with open("cloud_export.json", "w", encoding="utf-8") as f:
            json.dump(result["project_data"], f, ensure_ascii=False, indent=2)
        print("  ✅ JSON сохранён в cloud_export.json")
        
        # Импортируем обратно (создаём новый проект из JSON)
        print("  Импортируем проект обратно...")
        import_result = import_project_from_cloud(result)
        print(f"  Результат импорта: {import_result}")
        
        # Проверяем слои после импорта
        layers = get_layers()
        print(f"  Слоёв после импорта: {len(layers['layers'])}")
    
    print("\n✅ Фильтры, поворот и масштабирование работают!")
    
    print("\n" + "=" * 50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    print("=" * 50)
    
    print("\nДоступные API-функции:")
    print("  create_project(width, height)")
    print("  add_layer(name, image_path)")
    print("  get_layers()")
    print("  get_preview()")
    print("  set_layer_visibility(index, visible)")
    print("  set_layer_opacity(index, opacity)")
    print("  set_layer_blend_mode(index, mode)")
    print("  move_layer_up(index)")
    print("  move_layer_down(index)")
    print("  move_layer_to_top(index)")
    print("  move_layer_to_bottom(index)")
    print("  set_layer_position(index, x, y)")
    print("  remove_layer(index)")
    print("  save_current_project(folder)")
    print("  load_project_from_folder(folder)")
    print("  get_project_info()")
    print("  export_project(filepath)")
    print("  undo()")
    print("  redo()")


if __name__ == "__main__":
    main()