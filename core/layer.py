from PIL import Image
from typing import Optional

class Layer:
    def __init__(self, name: str, image: Optional[Image.Image] = None):
        self.name = name
        self.image = image if image else Image.new('RGBA', (800, 600), (255, 255, 255, 0))
        self.visible = True
        self.opacity = 100
        self.blend_mode = "normal"
        self.x = 0
        self.y = 0
        self.locked = False

    def set_visibility(self, visible: bool):
        self.visible = visible

    def set_opacity(self, opacity: int):
        self.opacity = max(0, min(100, opacity))

    def set_blend_mode(self, mode: str):
        if mode in ["normal", "multiply", "screen"]:
            self.blend_mode = mode

BLEND_MODES = {
    "normal": lambda bg, fg: fg,
    "multiply": lambda bg, fg: tuple(int(b * f / 255) for b, f in zip(bg[:3], fg[:3])) + (fg[3],),
    "screen": lambda bg, fg: tuple(255 - int((255 - b) * (255 - f) / 255) for b, f in zip(bg[:3], fg[:3])) + (fg[3],),
}