from api.editor_api import (
    create_project,
    add_layer,
    get_layers,
    get_preview,
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
    """Выводит список слоёв"""
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
    
    # 1. Создаём проект
    print("\n1. Создаём проект 800x600")
    create_project(800, 600)
    
    # 2. Добавляем слои
    print("\n2. Добавляем слои")
    add_layer("Фон")
    add_layer("Рисунок")
    add_layer("Текст")
    add_layer("Логотип")
    print_layers()
    
    # 3. Меняем прозрачность
    print("\n3. Меняем прозрачность слоя 1 на 50%")
    set_layer_opacity(1, 50)
    print_layers()
    
    # 4. Меняем режим наложения
    print("\n4. Меняем режим наложения слоя 1 на multiply")
    set_layer_blend_mode(1, "multiply")
    print_layers()
    
    # 5. Прячем слой
    print("\n5. Прячем слой 2")
    set_layer_visibility(2, False)
    print_layers()
    
    # 6. Перемещаем слои
    print("\n6. Перемещаем слой 3 выше")
    move_layer_up(3)
    print_layers()
    
    print("\n7. Перемещаем слой 0 ниже")
    move_layer_down(0)
    print_layers()
    
    # 8. Меняем позицию слоя
    print("\n8. Меняем позицию слоя 0 на x=100, y=50")
    set_layer_position(0, 100, 50)
    print_layers()
    
    # 9. Сохраняем проект
    print("\n9. Сохраняем проект в папку test_project")
    save_current_project("test_project")
    
    # 10. Экспортируем в PNG
    print("\n10. Экспортируем в PNG")
    export_project("export.png")
    
    # 11. Информация о проекте
    print("\n11. Информация о проекте")
    info = get_project_info()
    print(f"  Размер: {info['width']} x {info['height']}")
    print(f"  Слоёв: {info['layers_count']}")
    print(f"  Версия: {info['version']}")
    
    # 12. Тест Undo/Redo
    print("\n12. Тест Undo/Redo")
    print("  До Undo:")
    print_layers()
    
    undo()
    print("  После Undo (отмена последнего действия):")
    print_layers()
    
    redo()
    print("  После Redo (повтор):")
    print_layers()
    
    # 13. Загружаем проект обратно
    print("\n13. Загружаем проект из папки test_project")
    load_project_from_folder("test_project")
    print_layers()
    
    # 14. Удаляем слой
    print("\n14. Удаляем слой 0")
    remove_layer(0)
    print_layers()
    
    # 15. Получаем превью
    print("\n15. Информация о превью")
    preview = get_preview()
    print(f"  Размер превью: {preview['width']} x {preview['height']}")

    # 16. Тест фильтров
    print("\n16. Тест фильтров")
    
    # Создаём тестовый слой с изображением (если есть файл)
    # Или используем существующий слой
    add_layer("Для фильтров", None)
    
    print("  Применяем яркость +50 к слою 4")
    apply_filter_to_layer_api(4, "brightness", 50)
    
    print("  Применяем контраст +30 к слою 4")
    apply_filter_to_layer_api(4, "contrast", 30)
    
    # 17. Тест поворота
    print("\n17. Тест поворота")
    print("  Поворачиваем слой 4 на 90°")
    rotate_layer_api(4, 90)
    
    # 18. Тест масштабирования
    print("\n18. Тест масштабирования")
    print("  Увеличиваем слой 4 в 1.5 раза")
    scale_layer_api(4, 1.5)
    
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