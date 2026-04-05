"""
История действий для Ctrl+Z / Ctrl+Y
"""

from collections import deque
import copy
from typing import Optional, Any


class History:
    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.undo_stack: deque = deque(maxlen=max_size)
        self.redo_stack: deque = deque(maxlen=max_size)
    
    def push(self, state: Any) -> None:
        """Сохраняет состояние в историю"""
        # Делаем глубокую копию, чтобы не было ссылок
        state_copy = copy.deepcopy(state)
        self.undo_stack.append(state_copy)
        # При новом действии очищаем redo
        self.redo_stack.clear()
    
    def undo(self) -> Optional[Any]:
        """Отменяет последнее действие"""
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            return copy.deepcopy(state)
        return None
    
    def redo(self) -> Optional[Any]:
        """Повторяет отменённое действие"""
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            return copy.deepcopy(state)
        return None
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """Очищает историю"""
        self.undo_stack.clear()
        self.redo_stack.clear()