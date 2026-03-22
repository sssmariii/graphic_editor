from api.editor_api import create_project, add_layer, save_current_project, load_project_from_folder, get_layers

# Создаём проект
create_project()
add_layer("Тестовый слой")
add_layer("Ещё слой")

print("Слои до сохранения:", get_layers()["layers"])

# Сохраняем
save_current_project("test_project")
print("Проект сохранён в test_project/")

# Загружаем
load_project_from_folder("test_project")
print("Проект загружен")

print("Слои после загрузки:", get_layers()["layers"])