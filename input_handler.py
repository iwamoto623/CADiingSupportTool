import tkinter as tk
from shapes.ellipse import Ellipse

MIN_SIZE = 5  # これ以下のドラッグは無視


class InputHandler:
    def __init__(self, overlay, app):
        self._event_canvas = overlay.event_canvas
        self._canvas = overlay.canvas
        self.app = app

        self._editor = None         # 現在の ShapeEditor（選択中のみ存在）
        self._dragging_handle = False
        self._start_x = 0.0
        self._start_y = 0.0
        self._preview_id = None
        self._dragging = False

        self._event_canvas.bind('<Button-1>', self._on_press)
        self._event_canvas.bind('<B1-Motion>', self._on_drag)
        self._event_canvas.bind('<ButtonRelease-1>', self._on_release)
        self._event_canvas.bind('<Delete>', self._on_delete)
        self._event_canvas.bind('<Escape>', self._on_escape)

    # -----------------------------------------------------------------------
    # エディタ管理
    # -----------------------------------------------------------------------

    def set_editor(self, editor) -> None:
        """ShapeEditor を差し替える。None で解除。"""
        if self._editor:
            self._editor.clear()
        self._editor = editor
        if editor:
            editor.draw_handles()

    # -----------------------------------------------------------------------
    # マウスイベント
    # -----------------------------------------------------------------------

    def _on_press(self, event):
        if self.app.mode != 'draw':
            return

        # 1. ハンドルのヒットテストを最優先
        if self._editor:
            handle = self._editor.hit_test(event.x, event.y)
            if handle:
                self._editor.start_drag(handle, event.x, event.y)
                self._dragging_handle = True
                return

        # 2. 既存図形のクリック判定
        for shape in reversed(self.app.shapes):
            if shape.contains(event.x, event.y):
                if shape is not self.app.selected_shape:
                    self.app.select_shape(shape)
                return  # 図形上クリックなので新規作成しない

        # 3. 空領域クリック → 選択解除 + 新規作成開始
        self.app.deselect_shape()
        self._start_x = event.x
        self._start_y = event.y
        self._dragging = True

    def _on_drag(self, event):
        if self.app.mode != 'draw':
            return

        if self._dragging_handle and self._editor:
            self._editor.update_drag(event.x, event.y)
            return

        if not self._dragging:
            return

        if self._preview_id is not None:
            self._canvas.delete(self._preview_id)

        cx = (self._start_x + event.x) / 2
        cy = (self._start_y + event.y) / 2
        rx = abs(event.x - self._start_x) / 2
        ry = abs(event.y - self._start_y) / 2

        self._preview_id = self._canvas.create_oval(
            cx - rx, cy - ry, cx + rx, cy + ry,
            outline='white', width=1, dash=(4, 4), tags='preview',
        )

    def _on_release(self, event):
        if self.app.mode != 'draw':
            return

        if self._dragging_handle:
            self._dragging_handle = False
            if self._editor:
                self._editor.end_drag()
            return

        if not self._dragging:
            return
        self._dragging = False

        if self._preview_id is not None:
            self._canvas.delete(self._preview_id)
            self._preview_id = None

        cx = (self._start_x + event.x) / 2
        cy = (self._start_y + event.y) / 2
        rx = abs(event.x - self._start_x) / 2
        ry = abs(event.y - self._start_y) / 2

        if rx < MIN_SIZE or ry < MIN_SIZE:
            return

        self.app.add_shape(Ellipse(cx, cy, rx, ry))

    def _on_delete(self, event):
        self.app.delete_selected()

    def _on_escape(self, event):
        self._dragging = False
        self._dragging_handle = False
        if self._preview_id is not None:
            self._canvas.delete(self._preview_id)
            self._preview_id = None
        self.app.deselect_shape()
