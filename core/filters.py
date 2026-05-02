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