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
        self.history = History(max_size=20)  # Добавляем историю
        self._save_to_history()  # Сохраняем начальное состояние
    
    def _save_to_history(self):
        """Сохраняет текущее состояние в историю"""
        self.history.push(self._get_state())
    
    def _get_state(self) -> dict:
        """Возвращает копию текущего состояния"""
        return {
            "layers": copy.deepcopy(self.layers),
            "width": self.width,
            "height": self.height,
            "version": self.version
        }
    
    def _restore_state(self, state: dict):
        """Восстанавливает состояние из истории"""
        self.layers = state["layers"]
        self.width = state["width"]
        self.height = state["height"]
        self.version = state["version"]
    
    def undo(self) -> bool:
        """Отменяет последнее действие"""
        state = self.history.undo()
        if state:
            self._restore_state(state)
            return True
        return False
    
    def redo(self) -> bool:
        """Повторяет отменённое действие"""
        state = self.history.redo()
        if state:
            self._restore_state(state)
            return True
        return False
    
    # Обновляем методы, которые меняют состояние
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