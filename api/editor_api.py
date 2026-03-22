from core.project import Project
from core.layer import Layer
from core.canvas import render_preview
from core.file_manager import save_project, load_project
from PIL import Image
from typing import Dict, Any, Optional
import os
from core.canvas import export_to_png
from core.filters import apply_filter_to_layer
from core.filters import rotate_layer
from core.filters import scale_layer

_current_project: Optional[Project] = None

def create_project(width: int = 800, height: int = 600) -> Dict[str, Any]:
    """Создаёт новый проект"""
    global _current_project
    _current_project = Project(width, height)
    return {"status": "ok", "project_id": 1, "width": width, "height": height}


def add_layer(name: str, image_path: str = None) -> Dict[str, Any]:
    """Добавляет слой (из файла или пустой)"""
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    img = None
    if image_path:
        # Проверка 1: существует ли файл
        if not os.path.exists(image_path):
            return {"error": f"File not found: {image_path}"}
        
        # Проверка 2: правильное ли расширение
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            return {"error": f"Unsupported format: {ext}. Use PNG or JPG"}
        
        # Проверка 3: можно ли открыть файл
        try:
            img = Image.open(image_path).convert('RGBA')
        except Exception as e:
            return {"error": f"Cannot open image: {str(e)}"}
    
    layer = Layer(name, img)
    _current_project.add_layer(layer)
    return {"status": "ok", "layer_index": len(_current_project.layers) - 1}


def get_layers() -> Dict[str, Any]:
    """Возвращает список всех слоёв"""
    if _current_project is None:
        return {"layers": []}
    
    layers_data = []
    for i, layer in enumerate(_current_project.layers):
        layers_data.append({
            "index": i,
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode,
            "x": layer.x,
            "y": layer.y
        })
    return {"layers": layers_data}


def get_preview() -> Dict[str, Any]:
    """Возвращает информацию о превью"""
    if _current_project is None:
        return {"error": "No project"}
    
    preview = render_preview(_current_project)
    return {"width": preview.width, "height": preview.height}


def set_layer_visibility(layer_index: int, visible: bool) -> Dict[str, Any]:
    """Включает/выключает видимость слоя"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].set_visibility(visible)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def set_layer_opacity(layer_index: int, opacity: int) -> Dict[str, Any]:
    """Меняет прозрачность слоя (0-100)"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].set_opacity(opacity)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def set_layer_blend_mode(layer_index: int, blend_mode: str) -> Dict[str, Any]:
    """Устанавливает режим наложения слоя"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].set_blend_mode(blend_mode)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def move_layer_up(layer_index: int) -> Dict[str, Any]:
    """Перемещает слой выше"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_up(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer up"}


def move_layer_down(layer_index: int) -> Dict[str, Any]:
    """Перемещает слой ниже"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_down(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer down"}


def move_layer_to_top(layer_index: int) -> Dict[str, Any]:
    """Перемещает слой наверх"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_to_top(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer to top"}


def move_layer_to_bottom(layer_index: int) -> Dict[str, Any]:
    """Перемещает слой вниз"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_to_bottom(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer to bottom"}


def set_layer_position(layer_index: int, x: int, y: int) -> Dict[str, Any]:
    """Устанавливает позицию слоя"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].x = x
        _current_project.layers[layer_index].y = y
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def remove_layer(layer_index: int) -> Dict[str, Any]:
    """Удаляет слой"""
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.remove_layer(layer_index)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def save_current_project(folder_path: str) -> Dict[str, Any]:
    """Сохраняет текущий проект в папку"""
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    save_project(_current_project, folder_path)
    return {"status": "ok", "folder": folder_path}


def load_project_from_folder(folder_path: str) -> Dict[str, Any]:
    """Загружает проект из папки"""
    global _current_project
    _current_project = load_project(folder_path)
    return {"status": "ok", "project_id": 1}


def get_project_info() -> Dict[str, Any]:
    """Возвращает информацию о текущем проекте"""
    if _current_project is None:
        return {"error": "No active project"}
    
    return {
        "width": _current_project.width,
        "height": _current_project.height,
        "version": _current_project.version,
        "layers_count": len(_current_project.layers)
    }

def export_project(filepath: str) -> Dict[str, Any]:
    """Экспортирует текущий проект в PNG"""
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if export_to_png(_current_project, filepath):
        return {"status": "ok", "file": filepath}
    return {"error": "Export failed"}

def undo() -> Dict[str, Any]:
    """Отменяет последнее действие"""
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.undo():
        return {"status": "ok"}
    return {"error": "Nothing to undo"}

def redo() -> Dict[str, Any]:
    """Повторяет отменённое действие"""
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.redo():
        return {"status": "ok"}
    return {"error": "Nothing to redo"}

def apply_filter_to_layer_api(layer_index: int, filter_type: str, value: int) -> Dict[str, Any]:
    """
    Применяет фильтр к слою
    filter_type: "brightness" или "contrast"
    value: от -100 до 100
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        layer.image = apply_filter_to_layer(layer.image, filter_type, value)
        _current_project._save_to_history()
        return {"status": "ok", "filter": filter_type, "value": value}
    except Exception as e:
        return {"error": f"Failed to apply filter: {str(e)}"}
    
def rotate_layer_api(layer_index: int, angle: float) -> Dict[str, Any]:
    """
    Поворачивает слой на заданный угол
    angle: 90, 180, 270 или любое другое число
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        layer.image = rotate_layer(layer.image, angle)
        _current_project._save_to_history()
        return {"status": "ok", "angle": angle}
    except Exception as e:
        return {"error": f"Failed to rotate: {str(e)}"}

def scale_layer_api(layer_index: int, scale_x: float, scale_y: float = None) -> Dict[str, Any]:
    """
    Масштабирует слой
    scale_x: 0.5 = уменьшить вдвое, 2.0 = увеличить вдвое
    scale_y: если не указан, равен scale_x
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        old_width, old_height = layer.image.size
        layer.image = scale_layer(layer.image, scale_x, scale_y)
        new_width, new_height = layer.image.size
        
        # Корректируем позицию слоя, чтобы он оставался примерно на том же месте
        layer.x = int(layer.x * (new_width / old_width))
        layer.y = int(layer.y * (new_height / old_height))
        
        _current_project._save_to_history()
        return {"status": "ok", "scale_x": scale_x, "scale_y": scale_y or scale_x}
    except Exception as e:
        return {"error": f"Failed to scale: {str(e)}"}

def apply_filter_to_layer_api(layer_index: int, filter_type: str, value: int) -> Dict[str, Any]:
    """
    Применяет фильтр к слою
    filter_type: "brightness" или "contrast"
    value: от -100 до 100
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        layer.image = apply_filter_to_layer(layer.image, filter_type, value)
        _current_project._save_to_history()
        return {"status": "ok", "filter": filter_type, "value": value}
    except Exception as e:
        return {"error": f"Failed to apply filter: {str(e)}"}


def rotate_layer_api(layer_index: int, angle: float) -> Dict[str, Any]:
    """
    Поворачивает слой на заданный угол
    angle: 90, 180, 270 или любое другое число
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        layer.image = rotate_layer(layer.image, angle)
        _current_project._save_to_history()
        return {"status": "ok", "angle": angle}
    except Exception as e:
        return {"error": f"Failed to rotate: {str(e)}"}


def scale_layer_api(layer_index: int, scale_x: float, scale_y: float = None) -> Dict[str, Any]:
    """
    Масштабирует слой
    scale_x: 0.5 = уменьшить вдвое, 2.0 = увеличить вдвое
    scale_y: если не указан, равен scale_x
    """
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        old_width, old_height = layer.image.size
        layer.image = scale_layer(layer.image, scale_x, scale_y)
        new_width, new_height = layer.image.size
        
        # Корректируем позицию слоя
        layer.x = int(layer.x * (new_width / old_width))
        layer.y = int(layer.y * (new_height / old_height))
        
        _current_project._save_to_history()
        return {"status": "ok", "scale_x": scale_x, "scale_y": scale_y or scale_x}
    except Exception as e:
        return {"error": f"Failed to scale: {str(e)}"}