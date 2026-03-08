import math
from .base_shape import BaseShape


class Ellipse(BaseShape):
    def __init__(self, x: float = 0.0, y: float = 0.0,
                 radius_x: float = 50.0, radius_y: float = 30.0):
        super().__init__()
        self.x = x
        self.y = y
        self.radius_x = radius_x
        self.radius_y = radius_y

    def _get_points(self, steps: int = 60) -> list:
        angle_rad = math.radians(self.rotation)
        points = []
        for i in range(steps):
            t = 2 * math.pi * i / steps
            px = self.radius_x * math.cos(t)
            py = self.radius_y * math.sin(t)
            rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            points.extend([self.x + rx, self.y + ry])
        return points

    def draw(self, canvas) -> None:
        if not self.visible:
            return
        points = self._get_points()
        canvas.create_polygon(
            points,
            outline=self.color,
            fill='',
            width=self.line_width,
            smooth=True,
            tags='shape',
        )

    def contains(self, x: float, y: float) -> bool:
        angle_rad = math.radians(-self.rotation)
        dx = x - self.x
        dy = y - self.y
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        if self.radius_x == 0 or self.radius_y == 0:
            return False
        return (rx / self.radius_x) ** 2 + (ry / self.radius_y) ** 2 <= 1.0

    def get_params(self) -> dict:
        params = super().get_params()
        params.update({
            'radius_x': self.radius_x,
            'radius_y': self.radius_y,
        })
        return params
