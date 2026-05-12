"""
AI-инструменты для графического редактора (Pollinations.ai + локальная генерация).
"""

import requests
import base64
from PIL import Image
import io

def generate_image(prompt: str, style: str = "photo") -> dict:
    """
    Генерация изображения через Pollinations.ai.
    
    Args:
        prompt: текстовое описание
        style: "photo" (реалистичное) или "art" (художественное)
    
    Returns:
        {"ok": True, "image_base64": "...", "prompt": "..."}
    """
    try:
        # Добавляем стилевые модификаторы
        if style == "photo":
            enhanced_prompt = f"{prompt}, realistic photo, high resolution, sharp focus, natural lighting, photograph, 8K"
        else:
            enhanced_prompt = f"{prompt}, digital art, illustration, vibrant colors"
        
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            return {
                "ok": True,
                "image_base64": image_base64,
                "prompt": prompt
            }
        else:
            return {"ok": False, "error": f"Ошибка API: {response.status_code}"}
    
    except Exception as e:
        return {"ok": False, "error": str(e)}

def generate_solid_background(color: str, width: int = 1024, height: int = 1024) -> dict:
    """
    Генерация идеального однотонного фона (локально, без API).
    
    Args:
        color: название цвета или HEX (например, "blue", "#85ADFF", "dark gray")
        width: ширина
        height: высота
    
    Returns:
        {"ok": True, "image_base64": "...", "color": "..."}
    """
    try:
        from PIL import ImageColor
        
        # Преобразуем название цвета в RGB
        rgb_color = ImageColor.getrgb(color)
        
        # Создаём изображение
        img = Image.new('RGB', (width, height), color=rgb_color)
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "ok": True,
            "image_base64": image_base64,
            "color": color
        }
    
    except Exception as e:
        return {"ok": False, "error": f"Ошибка: {str(e)}"}