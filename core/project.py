from typing import List
from core.layer import Layer
import copy
from core.history import History
class Project:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.layers: List[Layer] = []
        self.version = 1
        self.history = History(max_size=20)
        self._save_to_history()
    
    def _save_to_history(self):
        self.history.push(self._get_state())
    
    def _get_state(self) -> dict:
        return {
            "layers": copy.deepcopy(self.layers),
            "width": self.width,
            "height": self.height,
            "version": self.version
        }
    
    def _restore_state(self, state: dict):
        self.layers = state["layers"]
        self.width = state["width"]
        self.height = state["height"]
        self.version = state["version"]
    
    def undo(self) -> bool:
        current_state = self._get_state()
        state = self.history.undo(current_state)
        if state:
            self._restore_state(state)
            return True
        return False

    def redo(self) -> bool:
        state = self.history.redo()
        if state:
            self._restore_state(state)
            return True
        return False
    
    def add_layer(self, layer: Layer):
        self.layers.append(layer)
        self._save_to_history()
    
    def remove_layer(self, index: int):
        if 0 <= index < len(self.layers):
            del self.layers[index]
            self._save_to_history()
    
    def move_layer_up(self, index: int):
        if 0 <= index < len(self.layers) - 1:
            self.layers[index], self.layers[index + 1] = self.layers[index + 1], self.layers[index]
            self._save_to_history()
            return True
        return False
    
    def move_layer_down(self, index: int):
        if 0 < index < len(self.layers):
            self.layers[index], self.layers[index - 1] = self.layers[index - 1], self.layers[index]
            self._save_to_history()
            return True
        return False
    def move_layer_to_top(self, index: int):
        if 0 <= index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.append(layer)
            self._save_to_history()
            return True
        return False

    def move_layer_to_bottom(self, index: int):
        if 0 <= index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.insert(0, layer)
            self._save_to_history()
            return True
        return False
    
    def resize_canvas(self, new_width: int, new_height: int, anchor: str = "center") -> None:
    
        old_width, old_height = self.width, self.height
    
        if anchor == "center":
            dx = (new_width - old_width) // 2
            dy = (new_height - old_height) // 2
        elif anchor == "top-left":
            dx, dy = 0, 0
        elif anchor == "bottom-right":
            dx = new_width - old_width
            dy = new_height - old_height
        else:
            dx = (new_width - old_width) // 2
            dy = (new_height - old_height) // 2
    
        for layer in self.layers:
            layer.x += dx
            layer.y += dy
    
        self.width = new_width
        self.height = new_height
        self._save_to_history()