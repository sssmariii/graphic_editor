from core.project import Project
from core.layer import Layer
from core.canvas import render_preview
from core.file_manager import save_project, load_project
from PIL import Image
import base64
import io
from typing import Dict, Any, Optional
import os
from core.canvas import export_to_png
from core.filters import apply_filter_to_layer
from core.filters import rotate_layer
from core.filters import scale_layer
from core.filters import crop_layer
from core.filters import remove_background
from core.signals import progress_tracker
from core.canvas import render_preview
from core.filters import flood_fill
from PIL import ImageDraw
from PIL import ImageFont
import sys

_current_project: Optional[Project] = None

def create_project(width: int = 800, height: int = 600) -> Dict[str, Any]:
    global _current_project
    _current_project = Project(width, height)
    return {"status": "ok", "project_id": 1, "width": width, "height": height}


def add_layer(name: str, image_path: str = None) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    img = None
    if image_path:
        if not os.path.exists(image_path):
            return {"error": f"File not found: {image_path}"}
        
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            return {"error": f"Unsupported format: {ext}. Use PNG or JPG"}
        
        try:
            img = Image.open(image_path).convert('RGBA')
        except Exception as e:
            return {"error": f"Cannot open image: {str(e)}"}
    
    layer = Layer(name, img)
    _current_project.add_layer(layer)
    return {"status": "ok", "layer_index": len(_current_project.layers) - 1}


def get_layers() -> Dict[str, Any]:
    if _current_project is None:
        return {"layers": []}
    
    layers_data = []
    for i, layer in enumerate(_current_project.layers):
        layers_data.append({
            "index": i,
            "name": layer.name,
            "visible": layer.visible,
            "locked": layer.locked,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode,
            "x": layer.x,
            "y": layer.y
        })
    return {"layers": layers_data}


def get_preview() -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No project"}
    
    preview = render_preview(_current_project)
    return {"width": preview.width, "height": preview.height}


def set_layer_visibility(layer_index: int, visible: bool) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project._save_to_history()
        _current_project.layers[layer_index].set_visibility(visible)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def set_layer_opacity(layer_index: int, opacity: int) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project._save_to_history()
        _current_project.layers[layer_index].set_opacity(opacity)
        return {"status": "ok"}


def set_layer_blend_mode(layer_index: int, blend_mode: str) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project._save_to_history()
        _current_project.layers[layer_index].set_blend_mode(blend_mode)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def move_layer_up(layer_index: int) -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_up(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer up"}


def move_layer_down(layer_index: int) -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_down(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer down"}


def move_layer_to_top(layer_index: int) -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_to_top(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer to top"}


def move_layer_to_bottom(layer_index: int) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.move_layer_to_bottom(layer_index):
        return {"status": "ok"}
    return {"error": "Cannot move layer to bottom"}


def set_layer_position(layer_index: int, x: int, y: int) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project._save_to_history()
        _current_project.layers[layer_index].x = x
        _current_project.layers[layer_index].y = y
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def remove_layer(layer_index: int) -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.remove_layer(layer_index)
        return {"status": "ok"}
    return {"error": "Invalid layer index"}


def save_current_project(folder_path: str) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    save_project(_current_project, folder_path)
    return {"status": "ok", "folder": folder_path}


def load_project_from_folder(folder_path: str) -> Dict[str, Any]:
    global _current_project
    _current_project = load_project(folder_path)
    return {"status": "ok", "project_id": 1}


def get_project_info() -> Dict[str, Any]:
    if _current_project is None:
        return {"error": "No active project"}
    
    return {
        "width": _current_project.width,
        "height": _current_project.height,
        "version": _current_project.version,
        "layers_count": len(_current_project.layers)
    }

def export_project(filepath: str) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if export_to_png(_current_project, filepath):
        return {"status": "ok", "file": filepath}
    return {"error": "Export failed"}

def undo() -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.undo():
        return {"status": "ok"}
    return {"error": "Nothing to undo"}


def redo() -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if _current_project.redo():
        return {"status": "ok"}
    return {"error": "Nothing to redo"}

def apply_filter_to_layer_api(layer_index: int, filter_type: str, value: int) -> Dict[str, Any]:
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
        
        layer.x = int(layer.x * (new_width / old_width))
        layer.y = int(layer.y * (new_height / old_height))
        
        _current_project._save_to_history()
        return {"status": "ok", "scale_x": scale_x, "scale_y": scale_y or scale_x}
    except Exception as e:
        return {"error": f"Failed to scale: {str(e)}"}

def export_project_to_cloud() -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    project_data = {
        "width": _current_project.width,
        "height": _current_project.height,
        "version": _current_project.version,
        "layers": []
    }
    
    for i, layer in enumerate(_current_project.layers):
        layer_data = {
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode,
            "x": layer.x,
            "y": layer.y,
            "image_base64": None
        }
        
        if layer.image is not None:
            buffer = io.BytesIO()
            layer.image.save(buffer, format="PNG")
            buffer.seek(0)
            layer_data["image_base64"] = base64.b64encode(buffer.read()).decode("utf-8")
        
        project_data["layers"].append(layer_data)
    
    return {"status": "ok", "project_data": project_data}


def import_project_from_cloud(json_data: Dict[str, Any]) -> Dict[str, Any]:
    global _current_project
    
    try:
        project_info = json_data.get("project_data", json_data)
        
        _current_project = Project(
            project_info.get("width", 800),
            project_info.get("height", 600)
        )
        _current_project.version = project_info.get("version", 1)
        
        for layer_data in project_info.get("layers", []):
            image = None
            if layer_data.get("image_base64"):
                image_bytes = base64.b64decode(layer_data["image_base64"])
                image_buffer = io.BytesIO(image_bytes)
                image = Image.open(image_buffer).convert('RGBA')
            
            layer = Layer(layer_data["name"], image)
            layer.visible = layer_data.get("visible", True)
            layer.opacity = layer_data.get("opacity", 100)
            layer.blend_mode = layer_data.get("blend_mode", "normal")
            layer.x = layer_data.get("x", 0)
            layer.y = layer_data.get("y", 0)
            
            _current_project.add_layer(layer)
        
        _current_project._save_to_history()
        return {"status": "ok", "project_id": 1, "layers_count": len(_current_project.layers)}
    
    except Exception as e:
        return {"error": f"Failed to import project: {str(e)}"}


def crop_layer_api(layer_index: int, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}

    offset_x = layer.x
    offset_y = layer.y
    local_x = x - offset_x
    local_y = y - offset_y

    img_width, img_height = layer.image.size
    
    crop_x = max(0, min(local_x, img_width - 1))
    crop_y = max(0, min(local_y, img_height - 1))
    crop_w = max(1, min(width, img_width - crop_x))
    crop_h = max(1, min(height, img_height - crop_y))

    if crop_w <= 0 or crop_h <= 0:
        return {"error": "Invalid crop dimensions"}

    try:
        cropped = layer.image.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        layer.image = cropped
        
        _current_project._save_to_history()
        return {"status": "ok", "new_width": cropped.width, "new_height": cropped.height}
    except Exception as e:
        return {"error": f"Failed to crop: {str(e)}"}


def import_psd(filepath: str) -> Dict[str, Any]:
    global _current_project
    try:
        from psd_tools import PSDImage
        psd = PSDImage.open(filepath)
        _current_project = Project(psd.width, psd.height)

        added = 0

        def add_layer_recursive(layer, parent_x=0, parent_y=0):
            nonlocal added
            
            off_x = parent_x + (layer.offset[0] if hasattr(layer, 'offset') else 0)
            off_y = parent_y + (layer.offset[1] if hasattr(layer, 'offset') else 0)

            
            if hasattr(layer, 'is_group') and layer.is_group():
                for child in layer:
                    add_layer_recursive(child, off_x, off_y)
                return

            
            img = None
            if hasattr(layer, 'composite'):
                img = layer.composite()
            if img is None and hasattr(layer, 'topil'):
                img = layer.topil()
            if img is None and hasattr(layer, 'as_PIL'):
                img = layer.as_PIL()

            if img is None:
                print(f"Warning: layer '{layer.name}' has no image data")
                return

            
            try:
                pil_img = img.convert('RGBA')
            except:
                pil_img = img

            new_layer = Layer(layer.name or f"Слой {added+1}", pil_img)
            new_layer.x = off_x
            new_layer.y = off_y
            new_layer.opacity = int(layer.opacity * 100) if hasattr(layer, 'opacity') else 100
            new_layer.visible = layer.visible if hasattr(layer, 'visible') else True
            _current_project.add_layer(new_layer)
            added += 1
            print(f"Added layer: {layer.name}, offset=({off_x},{off_y})")

        
        for layer in psd:
            add_layer_recursive(layer)

        print(f"Total layers added: {added}")
        _current_project._save_to_history()
        return {"status": "ok", "layers": added, "width": psd.width, "height": psd.height}

    except ImportError:
        return {"error": "psd-tools not installed. Run: pip install psd-tools"}
    except Exception as e:
        return {"error": f"Failed to import PSD: {str(e)}"}

from core.canvas import export_to_pdf

def export_to_pdf_api(filepath: str) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if export_to_pdf(_current_project, filepath):
        return {"status": "ok", "file": filepath}
    return {"error": "PDF export failed"}

def remove_background_api(layer_index: int, threshold: int = 128) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        layer.image = remove_background(layer.image, threshold)
        _current_project._save_to_history()
        return {"status": "ok"}
    except Exception as e:
        return {"error": f"Failed to remove background: {str(e)}"}
    
def register_progress_callback(callback) -> Dict[str, Any]:
    progress_tracker.register_callback(callback)
    return {"status": "ok"}


def get_progress_info() -> Dict[str, Any]:
    return {"status": "ok", "message": "Progress tracking available"}

def get_combined_image() -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No project"}
    
    img = render_preview(_current_project)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return {"status": "ok", "image_base64": image_base64, "width": img.width, "height": img.height}

def set_layer_locked(layer_index: int, locked: bool) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if 0 <= layer_index < len(_current_project.layers):
        _current_project.layers[layer_index].locked = locked
        _current_project._save_to_history()
        return {"status": "ok", "locked": locked}
    return {"error": "Invalid layer index"}

def draw_on_layer(layer_index: int, x: int, y: int, color: str, size: int = 5) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    
    if layer.locked:
        return {"error": "Layer is locked"}
    
    if layer.image is None:
        layer.image = Image.new('RGBA', (_current_project.width, _current_project.height), (0, 0, 0, 0))
    
    try:
        draw = ImageDraw.Draw(layer.image)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color, outline=color)
        _current_project._save_to_history()
        return {"status": "ok", "x": x, "y": y, "color": color, "size": size}
    except Exception as e:
        return {"error": f"Failed to draw: {str(e)}"}


def draw_line_on_layer(layer_index: int, x1: int, y1: int, x2: int, y2: int, color: str, size: int = 5) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    
    if layer.locked:
        return {"error": "Layer is locked"}
    
    if layer.image is None:
        layer.image = Image.new('RGBA', (_current_project.width, _current_project.height), (0, 0, 0, 0))
    
    try:
        draw = ImageDraw.Draw(layer.image)
        draw.line([x1, y1, x2, y2], fill=color, width=size)
        _current_project._save_to_history()
        return {"status": "ok"}
    except Exception as e:
        return {"error": f"Failed to draw line: {str(e)}"}
    
def draw_text_on_layer(layer_index: int, x: int, y: int, text: str, color: str, size: int = 20) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    
    if layer.locked:
        return {"error": "Layer is locked"}
    
    if layer.image is None:
        layer.image = Image.new('RGBA', (_current_project.width, _current_project.height), (0, 0, 0, 0))
    
    try:
        font = None
        
        if sys.platform == 'darwin':
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
            except:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
        elif sys.platform == 'win32':
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                try:
                    font = ImageFont.truetype("segoeui.ttf", size)
                except:
                    font = ImageFont.load_default()
        else:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            except:
                font = ImageFont.load_default()
        
        if font is None:
            font = ImageFont.load_default()
        
        scale = 2
        temp_width = len(text) * size * scale
        temp_height = int(size * 2 * scale)
        
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        temp_draw.text((5 * scale, 5 * scale), text, fill=color, font=font)
        
        new_width = int(temp_width / scale)
        new_height = int(temp_height / scale)
        temp_img = temp_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        layer.image.paste(temp_img, (x, y), temp_img)
        
        _current_project._save_to_history()
        
        return {"status": "ok", "text": text, "position": (x, y), "size": size}
    
    except Exception as e:
        return {"error": f"Failed to draw text: {str(e)}"}
    
def erase_on_layer(layer_index: int, x: int, y: int, size: int = 10) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    
    if layer.locked:
        return {"error": "Layer is locked"}
    
    if layer.image is None:
        layer.image = Image.new('RGBA', (_current_project.width, _current_project.height), (0, 0, 0, 0))
    
    try:
        draw = ImageDraw.Draw(layer.image, 'RGBA')
        transparent = (0, 0, 0, 0)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=transparent, outline=transparent)
        _current_project._save_to_history()
        return {"status": "ok", "x": x, "y": y, "size": size}
    except Exception as e:
        return {"error": f"Failed to erase: {str(e)}"}

def flood_fill_api(layer_index: int, x: int, y: int, new_color: str, tolerance: int = 0) -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    if not (0 <= layer_index < len(_current_project.layers)):
        return {"error": "Invalid layer index"}
    
    layer = _current_project.layers[layer_index]
    
    if layer.locked:
        return {"error": "Layer is locked"}
    
    if layer.image is None:
        return {"error": "Layer has no image"}
    
    try:
        new_color = new_color.lstrip('#')
        if len(new_color) == 6:
            new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            return {"error": f"Invalid color format: {new_color}. Use #RRGGBB"}
        
        _current_project._save_to_history()
        
        layer.image = flood_fill(layer.image, x, y, new_color_rgb, tolerance)
        
        return {"status": "ok", 
                "x": x, "y": y, 
                "new_color": new_color, 
                "tolerance": tolerance}
    
    except Exception as e:
        return {"error": f"Failed to flood fill: {str(e)}"}


def resize_canvas_api(new_width: int, new_height: int, anchor: str = "center") -> Dict[str, Any]:
    global _current_project
    if _current_project is None:
        return {"error": "No active project"}
    
    try:
        _current_project.resize_canvas(new_width, new_height, anchor)
        return {"status": "ok", "width": new_width, "height": new_height}
    except Exception as e:
        return {"error": f"Failed to resize canvas: {str(e)}"}