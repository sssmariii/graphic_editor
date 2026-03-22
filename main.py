from api.editor_api import (
    create_project,
    add_layer,
    get_layers,
    set_layer_visibility,
    set_layer_opacity,
    set_layer_blend_mode,
    move_layer_up,
    move_layer_down,
)

if __name__ == "__main__":
    # Создаём проект
    create_project(800, 600)
    print("Проект создан")
    
    # Добавляем слои
    add_layer("Фон")
    add_layer("Рисунок")
    add_layer("Текст")
    print("Слои добавлены")
    
    # Показываем слои
    print("\nСлои:")
    for layer in get_layers()["layers"]:
        print(f"  {layer['index']}: {layer['name']} | видим: {layer['visible']} | прозр: {layer['opacity']}% | режим: {layer['blend_mode']}")
    
    # Меняем прозрачность
    set_layer_opacity(1, 50)
    print("\nПрозрачность слоя 1 изменена на 50%")
    
    # Меняем режим наложения
    set_layer_blend_mode(1, "multiply")
    print("Режим слоя 1 изменён на multiply")
    
    # Прячем слой
    set_layer_visibility(2, False)
    print("Слой 2 скрыт")
    
    # Перемещаем слои
    move_layer_up(2)
    print("Слой 2 перемещён вверх")
    
    # Финальный список
    print("\nФинальные слои:")
    for layer in get_layers()["layers"]:
        print(f"  {layer['index']}: {layer['name']} | видим: {layer['visible']} | прозр: {layer['opacity']}% | режим: {layer['blend_mode']}")
    
    print("\n✅ Бэкенд работает")