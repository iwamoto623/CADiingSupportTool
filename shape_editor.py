import math
import tkinter as tk

HANDLE_RADIUS = 6    # ハンドルの表示半径（px）
HIT_RADIUS = HANDLE_RADIUS + 4  # クリック判定半径

# ハンドルの定義（名前: 表示色）
HANDLE_STYLES = {
    'move':     '#4a90d9',  # 青: 移動
    'radius_x': '#2ecc71',  # 緑: 長軸リサイズ
    'radius_y': '#e67e22',  # 橙: 短軸リサイズ
    'rotation': '#9b59b6',  # 紫: 回転
}


class ShapeEditor:
    """
    選択中の図形にドラッグハンドルを表示し、マウスで直接編集できるようにする。
    ハンドルは visual_canvas に描画される。
    マウス座標は event_canvas から来るが、両キャンバスは同じ座標系なので変換不要。
    """

    def __init__(self, shape, visual_canvas: tk.Canvas, on_change):
        self.shape = shape
        self._canvas = visual_canvas
        self._on_change = on_change
        self._handle_ids: list[int] = []
        self._active_handle: str | None = None
        self._drag_sx = 0.0
        self._drag_sy = 0.0
        self._orig: dict = {}

    # -----------------------------------------------------------------------
    # ハンドル位置の計算
    # -----------------------------------------------------------------------

    def _get_positions(self) -> dict[str, tuple[float, float]]:
        s = self.shape
        rot = math.radians(s.rotation)
        cx, cy = s.x, s.y
        cos_r, sin_r = math.cos(rot), math.sin(rot)
        return {
            'move':     (cx, cy),
            'radius_x': (cx + s.radius_x * cos_r,
                         cy + s.radius_x * sin_r),
            'radius_y': (cx - s.radius_y * sin_r,
                         cy + s.radius_y * cos_r),
            'rotation': (cx + (s.radius_x + 24) * cos_r,
                         cy + (s.radius_x + 24) * sin_r),
        }

    # -----------------------------------------------------------------------
    # 描画
    # -----------------------------------------------------------------------

    def draw_handles(self) -> None:
        self.clear()
        positions = self._get_positions()
        s = self.shape

        rx_pos  = positions['radius_x']
        ry_pos  = positions['radius_y']
        rot_pos = positions['rotation']
        cx, cy  = s.x, s.y

        # 補助線（中心 → 各ハンドル）
        for (x, y), color in (
            (rx_pos,  '#2ecc71'),
            (ry_pos,  '#e67e22'),
            (rot_pos, '#9b59b6'),
        ):
            self._handle_ids.append(
                self._canvas.create_line(
                    cx, cy, x, y,
                    fill=color, width=1, dash=(3, 3), tags='handle',
                )
            )

        # ハンドル本体
        for name, (hx, hy) in positions.items():
            r = HANDLE_RADIUS
            self._handle_ids.append(
                self._canvas.create_oval(
                    hx - r, hy - r, hx + r, hy + r,
                    fill=HANDLE_STYLES[name], outline='white', width=1.5,
                    tags='handle',
                )
            )

    def clear(self) -> None:
        for item_id in self._handle_ids:
            self._canvas.delete(item_id)
        self._handle_ids = []

    # -----------------------------------------------------------------------
    # ヒットテスト
    # -----------------------------------------------------------------------

    def hit_test(self, x: float, y: float) -> str | None:
        """クリック座標に最も近いハンドル名を返す。なければ None。"""
        positions = self._get_positions()
        # 優先順: rotation > radius_x > radius_y > move（重なり対策）
        for name in ('rotation', 'radius_x', 'radius_y', 'move'):
            hx, hy = positions[name]
            if math.hypot(x - hx, y - hy) <= HIT_RADIUS:
                return name
        return None

    # -----------------------------------------------------------------------
    # ドラッグ
    # -----------------------------------------------------------------------

    def start_drag(self, handle: str, x: float, y: float) -> None:
        self._active_handle = handle
        self._drag_sx = x
        self._drag_sy = y
        s = self.shape
        self._orig = {
            'x': s.x, 'y': s.y,
            'radius_x': s.radius_x, 'radius_y': s.radius_y,
            'rotation': s.rotation,
        }

    def update_drag(self, x: float, y: float) -> None:
        if not self._active_handle:
            return

        s = self.shape
        rot = math.radians(s.rotation)

        if self._active_handle == 'move':
            s.x = self._orig['x'] + (x - self._drag_sx)
            s.y = self._orig['y'] + (y - self._drag_sy)

        elif self._active_handle == 'radius_x':
            dx, dy = x - s.x, y - s.y
            proj = dx * math.cos(rot) + dy * math.sin(rot)
            s.radius_x = max(5.0, abs(proj))

        elif self._active_handle == 'radius_y':
            dx, dy = x - s.x, y - s.y
            proj = dx * (-math.sin(rot)) + dy * math.cos(rot)
            s.radius_y = max(5.0, abs(proj))

        elif self._active_handle == 'rotation':
            dx, dy = x - s.x, y - s.y
            s.rotation = math.degrees(math.atan2(dy, dx))

        self._on_change()

    def end_drag(self) -> None:
        self._active_handle = None
