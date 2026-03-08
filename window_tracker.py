import ctypes
import ctypes.wintypes
import tkinter as tk


class WindowTracker:
    """
    オプションモジュール。本体とは独立して動作する。
    対象ウィンドウの位置・サイズにオーバーレイを追従させる。
    """

    def __init__(self, target_hwnd: int, overlay, interval_ms: int = 100):
        self.target_hwnd = target_hwnd
        self.overlay = overlay
        self.interval_ms = interval_ms
        self._running = False

    def start(self) -> None:
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False

    def _tick(self) -> None:
        if not self._running:
            return

        user32 = ctypes.windll.user32

        if not user32.IsWindow(self.target_hwnd):
            self.stop()
            return

        if user32.IsIconic(self.target_hwnd):
            self.overlay.hide()
        else:
            self.overlay.show()
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(self.target_hwnd, ctypes.byref(rect))
            self.overlay.resize(
                rect.left, rect.top,
                rect.right - rect.left,
                rect.bottom - rect.top,
            )

        self.overlay._visual.after(self.interval_ms, self._tick)

    @staticmethod
    def pick_window(master: tk.Tk) -> int | None:
        """実行中のウィンドウ一覧を表示してHWNDを返す。キャンセル時はNone。"""
        windows = []

        def enum_cb(hwnd, _):
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
                title = buf.value.strip()
                if title and title != 'CADEditTool':
                    windows.append((hwnd, title))
            return True

        cb_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        ctypes.windll.user32.EnumWindows(cb_type(enum_cb), 0)

        return _PickDialog(master, windows).result


class _PickDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk, windows: list):
        super().__init__(master)
        self.title('追従するウィンドウを選択')
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        tk.Label(self, text='追従するアプリを選んでください：', pady=8).pack()

        frame = tk.Frame(self)
        frame.pack(fill='both', padx=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        self._listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=60, height=15)
        self._listbox.pack(side='left', fill='both')
        scrollbar.config(command=self._listbox.yview)

        self._windows = windows
        for _, title in windows:
            self._listbox.insert('end', title)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text='選択', command=self._on_select, width=10).pack(side='left', padx=4)
        tk.Button(btn_frame, text='キャンセル', command=self.destroy, width=10).pack(side='left', padx=4)

        self._listbox.bind('<Double-Button-1>', lambda _: self._on_select())
        self.wait_window()

    def _on_select(self):
        sel = self._listbox.curselection()
        if sel:
            self.result = self._windows[sel[0]][0]
        self.destroy()
