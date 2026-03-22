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
def export_to_png(project: Project, filepath: str) -> bool:
    """Экспортирует проект в PNG файл"""
    try:
        preview = render_preview(project)
        preview.save(filepath, "PNG")
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False