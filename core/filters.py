from PIL import Image, ImageEnhance


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    """
    Изменяет яркость изображения
    factor: 0.0 (чёрное) -> 1.0 (оригинал) -> 2.0 (ярче)
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    """
    Изменяет контраст изображения
    factor: 0.0 (серое) -> 1.0 (оригинал) -> 2.0 (больше контраста)
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def apply_filter_to_layer(image: Image.Image, filter_type: str, value: float) -> Image.Image:
    """
    Применяет фильтр к изображению слоя
    filter_type: "brightness" или "contrast"
    value: от -100 до 100 (преобразуется в factor)
    """
    
    factor = 1.0 + (value / 100.0)
    
    if filter_type == "brightness":
        return adjust_brightness(image, factor)
    elif filter_type == "contrast":
        return adjust_contrast(image, factor)
    
    return image

def rotate_layer(image: Image.Image, angle: float) -> Image.Image:
    """
    Поворачивает изображение на заданный угол
    angle: 90, 180, 270 или произвольный угол
    """
    # Для углов кратных 90 используем transpose (быстрее)
    if angle == 90:
        return image.transpose(Image.ROTATE_90)
    elif angle == 180:
        return image.transpose(Image.ROTATE_180)
    elif angle == 270:
        return image.transpose(Image.ROTATE_270)
    else:
        # Для произвольного угла используем rotate
        return image.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))

def scale_layer(image: Image.Image, scale_x: float, scale_y: float = None) -> Image.Image:
    """
    Масштабирует изображение
    scale_x: коэффициент по ширине (0.5 = половина, 2.0 = в два раза)
    scale_y: коэффициент по высоте (если None, то равен scale_x)
    """
    if scale_y is None:
        scale_y = scale_x
    
    new_width = int(image.width * scale_x)
    new_height = int(image.height * scale_y)
    
    # Не даём стать слишком маленьким или большим
    new_width = max(1, min(new_width, 5000))
    new_height = max(1, min(new_height, 5000))
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)