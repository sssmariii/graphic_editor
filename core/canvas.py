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
        
        blend_mode = layer.blend_mode
        box = (layer.x, layer.y, layer.x + img.width, layer.y + img.height)
        
        if blend_mode == "normal":
            result.paste(img, box, img)
        
        elif blend_mode == "multiply":
            bg_region = result.crop(box).copy()
            bg_data = bg_region.load()
            fg_data = img.load()
            
            for y in range(img.height):
                for x in range(img.width):
                    fg_r, fg_g, fg_b, fg_a = fg_data[x, y]
                    if fg_a == 0:
                        continue
                    bg_r, bg_g, bg_b, bg_a = bg_data[x, y]
                    
                    r = (fg_r * bg_r) // 255
                    g = (fg_g * bg_g) // 255
                    b = (fg_b * bg_b) // 255
                    a = (fg_a * bg_a) // 255
                    
                    bg_data[x, y] = (r, g, b, a)
            
            result.paste(bg_region, box)
        
        elif blend_mode == "screen":
            bg_region = result.crop(box).copy()
            bg_data = bg_region.load()
            fg_data = img.load()
            
            for y in range(img.height):
                for x in range(img.width):
                    fg_r, fg_g, fg_b, fg_a = fg_data[x, y]
                    if fg_a == 0:
                        continue
                    bg_r, bg_g, bg_b, bg_a = bg_data[x, y]
                    
                    r = 255 - ((255 - fg_r) * (255 - bg_r) // 255)
                    g = 255 - ((255 - fg_g) * (255 - bg_g) // 255)
                    b = 255 - ((255 - fg_b) * (255 - bg_b) // 255)
                    a = (fg_a * bg_a) // 255
                    
                    bg_data[x, y] = (r, g, b, a)
            
            result.paste(bg_region, box)
        
        else:
            result.paste(img, box, img)
    
    return result
def export_to_png(project: Project, filepath: str) -> bool:
    try:
        preview = render_preview(project)
        preview.save(filepath, "PNG")
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False

def export_to_pdf(project: Project, filepath: str) -> bool:
    try:
        from PIL import ImageDraw
        
        preview = render_preview(project)
        
        if preview.mode == 'RGBA':
            rgb_image = Image.new('RGB', preview.size, (255, 255, 255))
            rgb_image.paste(preview, mask=preview.split()[3])
            preview = rgb_image
        
        preview.save(filepath, "PDF", resolution=100.0)
        return True
    except Exception as e:
        print(f"PDF export error: {e}")
        return False
    
def render_preview_optimized(project: Project, max_size: int = 1024) -> Image.Image:
    scale = 1.0
    if project.width > max_size or project.height > max_size:
        scale = min(max_size / project.width, max_size / project.height)
    
    preview_width = int(project.width * scale)
    preview_height = int(project.height * scale)
    
    result = Image.new('RGBA', (preview_width, preview_height), (255, 255, 255, 255))
    
    from core.signals import progress_tracker
    
    for i, layer in enumerate(project.layers):
        if not layer.visible or layer.image is None:
            continue
        
        progress_tracker.update(i, len(project.layers), f"Rendering layer {layer.name}")
        
        img = layer.image.copy()
        if scale != 1.0:
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        if layer.opacity < 100:
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: p * layer.opacity // 100)
            img.putalpha(alpha)
        
        x = int(layer.x * scale)
        y = int(layer.y * scale)
        
        result.paste(img, (x, y), img)
    
    return result