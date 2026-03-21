from core.project import Project
from core.layer import Layer
from core.canvas import render_preview
from PIL import Image
from typing import Dict, Any

_current_project: Project = None

def create_project(width: int = 800, height: int = 600) -> Dict[str, Any]:
    """Создаёт новый проект"""
    global _current_project
    _current_project = Project(width, height)
    return {"status": "ok", "project_id": 1, "width": width, "height": height}

def add_layer(name: str, image_path: str = None) -> Dict[str, Any]:
    """Добавляет слой"""
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
    """Возвращает список слоёв"""
    if _current_project is None:
        return {"layers": []}
    
    layers_data = []
    for i, layer in enumerate(_current_project.layers):
        layers_data.append({
            "index": i,
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode
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
    if _current_project and 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].set_visibility(visible)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}

def set_layer_opacity(layer_index: int, opacity: int) -> Dict[str, Any]:
    """Меняет прозрачность слоя"""
    if _current_project and 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].set_opacity(opacity)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}