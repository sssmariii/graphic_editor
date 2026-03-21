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