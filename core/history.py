from collections import deque
import copy
from typing import Optional, Any


class History:
    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.undo_stack: deque = deque(maxlen=max_size)
        self.redo_stack: deque = deque(maxlen=max_size)
    
    def push(self, state: Any) -> None:
        state_copy = copy.deepcopy(state)
        self.undo_stack.append(state_copy)
        self.redo_stack.clear()
    
    def undo(self, current_state: Any) -> Optional[Any]:
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(copy.deepcopy(current_state))
            return copy.deepcopy(state)
        return None

    def redo(self) -> Optional[Any]:
        if self.redo_stack:
            state = self.redo_stack.pop()
            return copy.deepcopy(state)
        return None
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()