from PIL import Image
from core.project import Project

def render_preview(project: Project) -> Image.Image:
    result = Image.new('RGBA', (project.width, project.height), (255, 255, 255, 255))
    
    for layer in project.layers:
        if not layer.visible or layer.image is None:
            continue
        
        img = layer.image.copy()
        
        if layer.opacity < 100:
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: p * layer.opacity // 100)
            img.putalpha(alpha)
        
        result.paste(img, (layer.x, layer.y), img)
    
    return result