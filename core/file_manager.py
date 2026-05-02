import json
import os
from PIL import Image
from core.project import Project
from core.layer import Layer

def save_project(project: Project, folder_path: str):
    os.makedirs(folder_path, exist_ok=True)
    
    data = {
        "width": project.width,
        "height": project.height,
        "version": project.version,
        "layers": []
    }
    
    for i, layer in enumerate(project.layers):
        if layer.image:
            layer.image.save(f"{folder_path}/layer_{i}.png")
        
        data["layers"].append({
            "name": layer.name,
            "visible": layer.visible,
            "opacity": layer.opacity,
            "blend_mode": layer.blend_mode,
            "x": layer.x,
            "y": layer.y,
            "image_file": f"layer_{i}.png"
        })
    
    with open(f"{folder_path}/project.json", "w") as f:
        json.dump(data, f, indent=2)

def load_project(folder_path: str) -> Project:
    with open(f"{folder_path}/project.json", "r") as f:
        data = json.load(f)
    
    project = Project(data["width"], data["height"])
    project.version = data["version"]
    
    for layer_data in data["layers"]:
        image_path = f"{folder_path}/{layer_data['image_file']}"
        image = Image.open(image_path) if os.path.exists(image_path) else None
        
        layer = Layer(layer_data["name"], image)
        layer.visible = layer_data["visible"]
        layer.opacity = layer_data["opacity"]
        layer.blend_mode = layer_data["blend_mode"]
        layer.x = layer_data["x"]
        layer.y = layer_data["y"]
        
        project.add_layer(layer)
    
    return project