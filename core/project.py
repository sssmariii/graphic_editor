from typing import List
from core.layer import Layer

class Project:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.layers: List[Layer] = []
        self.version = 1

    def add_layer(self, layer: Layer):
        self.layers.append(layer)

    def remove_layer(self, index: int):
        if 0 <= index < len(self.layers):
            del self.layers[index]

    def get_layers(self) -> List[Layer]:
        return self.layers
    
    def move_layer_up(self, index: int):
        """Перемещает слой выше"""
        if 0 <= index < len(self.layers) - 1:
            self.layers[index], self.layers[index + 1] = self.layers[index + 1], self.layers[index]
            return True
        return False

    def move_layer_down(self, index: int):
        """Перемещает слой ниже"""
        if 0 < index < len(self.layers):
            self.layers[index], self.layers[index - 1] = self.layers[index - 1], self.layers[index]
            return True
        return False

    def move_layer_to_top(self, index: int):
        """Перемещает слой наверх"""
        if 0 <= index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.append(layer)
            return True
        return False

    def move_layer_to_bottom(self, index: int):
        """Перемещает слой вниз"""
        if 0 <= index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.insert(0, layer)
            return True
        return False