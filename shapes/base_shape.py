from abc import ABC, abstractmethod


class BaseShape(ABC):
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.rotation: float = 0.0
        self.color: str = 'red'
        self.line_width: int = 2
        self.visible: bool = True

    @abstractmethod
    def draw(self, canvas) -> None:
        pass

    @abstractmethod
    def contains(self, x: float, y: float) -> bool:
        pass

    def get_params(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'rotation': self.rotation,
            'color': self.color,
            'line_width': self.line_width,
            'visible': self.visible,
        }

    def set_params(self, params: dict) -> None:
        for k, v in params.items():
            if hasattr(self, k):
                setattr(self, k, v)
