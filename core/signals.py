class ProgressTracker:
    def __init__(self):
        self._callbacks = []
    
    def register_callback(self, callback):
        self._callbacks.append(callback)
    
    def update(self, current: int, total: int, message: str = ""):
        percent = int(current / total * 100) if total > 0 else 0
        for callback in self._callbacks:
            callback(percent, message)
    
    def clear(self):
        self._callbacks.clear()


progress_tracker = ProgressTracker()