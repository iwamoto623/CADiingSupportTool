import tkinter as tk


class ControlWindow:
    def __init__(self, master: tk.Tk, app):
        self.app = app
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.wm_attributes('-topmost', True)
        self.win.geometry('+10+10')

        self._drag_x = 0
        self._drag_y = 0

        self._build_ui()

        # ドラッグ移動はタイトルバー部分のみ
        self._title_bar.bind('<Button-1>', self._on_drag_start)
        self._title_bar.bind('<B1-Motion>', self._on_drag)
        self._title_label.bind('<Button-1>', self._on_drag_start)
        self._title_label.bind('<B1-Motion>', self._on_drag)

        # click_win（フルスクリーン）より常に前面に出るよう定期的に lift する
        self._keep_on_top()

    def _build_ui(self):
        outer = tk.Frame(self.win, bg='#2b2b2b', bd=1, relief='solid')
        outer.pack()

        self._title_bar = tk.Frame(outer, bg='#444', pady=4)
        self._title_bar.pack(fill='x')

        self._title_label = tk.Label(
            self._title_bar, text='CADEditTool', bg='#444', fg='white',
            font=('Segoe UI', 9, 'bold'), padx=8,
        )
        self._title_label.pack(side='left')

        btn_frame = tk.Frame(outer, bg='#2b2b2b', padx=8, pady=8)
        btn_frame.pack()

        self.mode_btn = tk.Button(
            btn_frame, text='背景透過モードへ',
            command=self.app.toggle_mode,
            bg='#4a90d9', fg='white', relief='flat',
            padx=10, pady=5, cursor='hand2',
        )
        self.mode_btn.pack(fill='x', pady=(0, 4))

        tk.Button(
            btn_frame, text='全消去',
            command=self.app.clear_shapes,
            bg='#c0392b', fg='white', relief='flat',
            padx=10, pady=5, cursor='hand2',
        ).pack(fill='x', pady=(0, 4))

        tk.Button(
            btn_frame, text='終了',
            command=self.app.quit,
            bg='#555', fg='white', relief='flat',
            padx=10, pady=5, cursor='hand2',
        ).pack(fill='x')

    def update_mode_button(self, mode: str) -> None:
        if mode == 'draw':
            self.mode_btn.config(text='背景透過モードへ', bg='#4a90d9')
        else:
            self.mode_btn.config(text='描画モードへ', bg='#27ae60')

    def _on_drag_start(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.win.winfo_x() + event.x - self._drag_x
        y = self.win.winfo_y() + event.y - self._drag_y
        self.win.geometry(f'+{x}+{y}')

    def _keep_on_top(self):
        self.win.lift()
        self.win.after(200, self._keep_on_top)
