from core.project import Project
from core.layer import Layer
from core.canvas import render_preview
from core.file_manager import save_project, load_project
from PIL import Image
from typing import Dict, Any, Optional

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
    
    if image_path:
        img = Image.open(image_path).convert('RGBA')
    else:
        img = None
    
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