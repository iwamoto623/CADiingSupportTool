import ctypes
import tkinter as tk
from tkinter import messagebox

from overlay_window import OverlayWindow
from control_window import ControlWindow
from input_handler import InputHandler
from param_window import ParamWindow
from shape_editor import ShapeEditor
from window_tracker import WindowTracker

# 高DPI環境での座標ずれを防止
ctypes.windll.user32.SetProcessDPIAware()


class App:
    def __init__(self):
        # root は非表示のコントローラ。全ウィンドウはこの Toplevel として管理する。
        self.root = tk.Tk()
        self.root.withdraw()

        self.shapes: list = []
        self.mode: str = 'draw'
        self.selected_shape = None
        self._param_window: ParamWindow | None = None
        self._tracker: WindowTracker | None = None

        # --- 起動時: 描画範囲を選択 ---
        self._ask_target_window()

        # --- 各コンポーネントを初期化 ---
        self.overlay = OverlayWindow(self.root, self)
        self.control = ControlWindow(self.root, self)
        self.input_handler = InputHandler(self.overlay, self)

        # --- window_tracker オプション ---
        if self._target_hwnd:
            self._tracker = WindowTracker(self._target_hwnd, self.overlay)
            self._tracker.start()

    def _ask_target_window(self):
        answer = messagebox.askyesno(
            'CADEditTool',
            '特定のウィンドウに追従しますか？\n\n'
            '「はい」→ 追従するウィンドウを選択\n'
            '「いいえ」→ フルスクリーンで起動',
        )

        if answer:
            hwnd = WindowTracker.pick_window(self.root)
            self._target_hwnd = hwnd
        else:
            self._target_hwnd = None

    # -----------------------------------------------------------------------
    # 描画
    # -----------------------------------------------------------------------

    def _redraw(self) -> None:
        """図形を再描画し、アクティブなハンドルも再描画する。"""
        self.overlay.redraw()
        if self.input_handler._editor:
            self.input_handler._editor.draw_handles()

    # -----------------------------------------------------------------------
    # 選択管理
    # -----------------------------------------------------------------------

    def select_shape(self, shape) -> None:
        self.deselect_shape()
        self.selected_shape = shape

        # ShapeEditor を作成して InputHandler に渡す
        editor = ShapeEditor(
            shape,
            self.overlay.canvas,
            self._on_shape_changed,
        )
        self.input_handler.set_editor(editor)

        # パラメータウィンドウを開く
        pwin = ParamWindow(
            self.root, shape,
            on_change=self._on_shape_changed,
            on_close=lambda: self._on_param_window_closed(),
        )
        self._param_window = pwin

    def deselect_shape(self) -> None:
        self.selected_shape = None
        self.input_handler.set_editor(None)
        if self._param_window:
            try:
                self._param_window.win.destroy()
            except tk.TclError:
                pass
            self._param_window = None
        self.overlay.redraw()

    def _on_shape_changed(self) -> None:
        """図形のパラメータが変更されたときに呼ばれる（ハンドル・入力欄どちらからでも）。"""
        self._redraw()
        if self._param_window:
            try:
                self._param_window.refresh()
            except tk.TclError:
                self._param_window = None

    def _on_param_window_closed(self) -> None:
        """パラメータウィンドウが閉じられたとき。"""
        self._param_window = None
        self.selected_shape = None
        self.input_handler.set_editor(None)
        self.overlay.redraw()

    # -----------------------------------------------------------------------
    # 公開メソッド
    # -----------------------------------------------------------------------

    def toggle_mode(self) -> None:
        if self.mode == 'draw':
            self.mode = 'transparent'
            self.overlay.set_clickthrough(True)
        else:
            self.mode = 'draw'
            self.overlay.set_clickthrough(False)
        self.control.update_mode_button(self.mode)

    def clear_shapes(self) -> None:
        self.deselect_shape()
        self.shapes.clear()
        self.overlay.redraw()

    def add_shape(self, shape) -> None:
        self.shapes.append(shape)
        self._redraw()

    def delete_selected(self) -> None:
        if self.selected_shape and self.selected_shape in self.shapes:
            self.shapes.remove(self.selected_shape)
        self.deselect_shape()

    def quit(self) -> None:
        if self._tracker:
            self._tracker.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == '__main__':
    App().run()
