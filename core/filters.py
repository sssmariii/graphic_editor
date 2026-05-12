from PIL import Image, ImageEnhance


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def apply_filter_to_layer(image: Image.Image, filter_type: str, value: float) -> Image.Image:
    
    factor = 1.0 + (value / 100.0)
    
    if filter_type == "brightness":
        return adjust_brightness(image, factor)
    elif filter_type == "contrast":
        return adjust_contrast(image, factor)
    
    return image

def rotate_layer(image: Image.Image, angle: float) -> Image.Image:
    
    if angle == 90:
        return image.transpose(Image.ROTATE_90)
    elif angle == 180:
        return image.transpose(Image.ROTATE_180)
    elif angle == 270:
        return image.transpose(Image.ROTATE_270)
    else:
        return image.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))

def scale_layer(image: Image.Image, scale_x: float, scale_y: float = None) -> Image.Image:
    
    if scale_y is None:
        scale_y = scale_x
    
    new_width = int(image.width * scale_x)
    new_height = int(image.height * scale_y)
    
    new_width = max(1, min(new_width, 5000))
    new_height = max(1, min(new_height, 5000))
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def crop_layer(image: Image.Image, x: int, y: int, width: int, height: int) -> Image.Image:
    
    x = max(0, min(x, image.width - 1))
    y = max(0, min(y, image.height - 1))
    width = min(width, image.width - x)
    height = min(height, image.height - y)
    
    if width <= 0 or height <= 0:
        return image
    
    return image.crop((x, y, x + width, y + height))

def remove_background(image: Image.Image, threshold: int = 128) -> Image.Image:
   
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    pixels = image.load()
    width, height = image.size
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r > threshold and g > threshold and b > threshold:
                pixels[x, y] = (r, g, b, 0)
    
    return image

def flood_fill(image: Image.Image, x: int, y: int, new_color_rgb: tuple, tolerance: int = 0) -> Image.Image:
    if image is None:
        raise ValueError("Image is None")
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    img = image.copy()
    pixels = img.load()
    width, height = img.size
    
    if x < 0 or x >= width or y < 0 or y >= height:
        return img
    
    target = pixels[x, y][:3]
    
    if target == new_color_rgb:
        return img
    
    stack = [(x, y)]
    visited = set()
    visited.add((x, y))
    
    while stack:
        cx, cy = stack.pop()
        
        current = pixels[cx, cy][:3]
        
        if tolerance > 0:
            diff = abs(current[0] - target[0]) + abs(current[1] - target[1]) + abs(current[2] - target[2])
            if diff > tolerance * 3:
                continue
        else:
            if current != target:
                continue
        
        pixels[cx, cy] = (new_color_rgb[0], new_color_rgb[1], new_color_rgb[2], 255)
        
        neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
        for nx, ny in neighbors:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append((nx, ny))
    
    return img