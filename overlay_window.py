import tkinter as tk
import ctypes

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

VISUAL_BG = '#000000'  # 透明色（視覚的に透明 + 常時クリック透過）


class OverlayWindow:
    """
    2ウィンドウ構成:
      visual_win : 図形描画用。透明背景 + 常時クリックスルー。
      click_win  : マウスイベント捕捉用。1%不透明（ほぼ見えない）。
                   描画モード時はクリックを受け取り、背景透過モード時は透過する。
    両ウィンドウは同じ位置・サイズに配置されるため座標系が一致する。
    """

    def __init__(self, master: tk.Tk, app):
        self.app = app

        w = master.winfo_screenwidth()
        h = master.winfo_screenheight()
        geo = f'{w}x{h}+0+0'

        # --- visual_win: 図形描画、常時クリックスルー ---
        self._visual = tk.Toplevel(master)
        self._visual.overrideredirect(True)
        self._visual.wm_attributes('-topmost', True)
        self._visual.wm_attributes('-transparentcolor', VISUAL_BG)
        self._visual.geometry(geo)

        self.canvas = tk.Canvas(self._visual, bg=VISUAL_BG, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self._visual.update()
        self._visual_hwnd = int(self._visual.wm_frame(), 16)
        self._set_style(self._visual_hwnd, click_through=True)

        # --- click_win: マウスイベント捕捉、1%不透明 ---
        self._click = tk.Toplevel(master)
        self._click.overrideredirect(True)
        self._click.wm_attributes('-topmost', True)
        self._click.wm_attributes('-alpha', 0.01)
        self._click.geometry(geo)

        self.event_canvas = tk.Canvas(self._click, bg='white', highlightthickness=0)
        self.event_canvas.pack(fill='both', expand=True)

        self._click.update()
        self._click_hwnd = int(self._click.wm_frame(), 16)
        self._set_style(self._click_hwnd, click_through=False)  # 描画モードで起動

    def _set_style(self, hwnd: int, click_through: bool) -> None:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if click_through:
            style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        else:
            style = (style | WS_EX_LAYERED) & ~WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def set_clickthrough(self, enabled: bool) -> None:
        self._set_style(self._click_hwnd, click_through=enabled)

    def redraw(self) -> None:
        self.canvas.delete('all')
        for shape in self.app.shapes:
            shape.draw(self.canvas)

    def show(self) -> None:
        # z-order を乱さないよう deiconify は使わない。
        # resize() が直後に呼ばれて正しい位置へ戻る。
        pass

    def hide(self) -> None:
        # withdraw/deiconify は z-order を変えるため使わない。
        # 画面外へ移動することで「非表示」を実現する。
        off = '1x1+-10000+-10000'
        self._visual.geometry(off)
        self._click.geometry(off)

    def resize(self, x: int, y: int, w: int, h: int) -> None:
        geo = f'{w}x{h}+{x}+{y}'
        self._visual.geometry(geo)
        self._click.geometry(geo)
