import tkinter as tk
from tkinter import colorchooser
from shapes.base_shape import BaseShape

# 表示ラベルの定義（順序付き）
PARAM_LABELS = [
    ('x',         'X座標',        'float'),
    ('y',         'Y座標',        'float'),
    ('radius_x',  '長軸半径',      'float'),
    ('radius_y',  '短軸半径',      'float'),
    ('rotation',  '回転角度 (°)', 'float'),
    ('color',     '線の色',        'color'),
    ('line_width','線の太さ',      'int'),
]


class ParamWindow:
    def __init__(self, master: tk.Tk, shape: BaseShape, on_change, on_close=None):
        self.shape = shape
        self.on_change = on_change

        self.win = tk.Toplevel(master)
        self.win.title(f'パラメータ - {shape.__class__.__name__}')
        self.win.wm_attributes('-topmost', True)
        self.win.resizable(False, False)

        self._drag_x = 0
        self._drag_y = 0
        self._vars: dict[str, tk.StringVar] = {}
        self._color_previews: dict[str, tk.Label] = {}
        self._refreshing = False  # refresh() 中はトレースを無視

        self._on_close = on_close
        self._build_ui()
        self.win.protocol('WM_DELETE_WINDOW', self._on_delete_window)

    def _on_delete_window(self):
        if self._on_close:
            self._on_close()
        try:
            self.win.destroy()
        except tk.TclError:
            pass

    def _build_ui(self):
        outer = tk.Frame(self.win, bg='#2b2b2b', bd=1, relief='solid')
        outer.pack(fill='both', expand=True)

        title_bar = tk.Frame(outer, bg='#444', pady=4)
        title_bar.pack(fill='x')
        title_lbl = tk.Label(
            title_bar, text=f'  {self.shape.__class__.__name__}',
            bg='#444', fg='white', font=('Segoe UI', 9, 'bold'),
        )
        title_lbl.pack(side='left')

        title_bar.bind('<Button-1>', self._on_drag_start)
        title_bar.bind('<B1-Motion>', self._on_drag)
        title_lbl.bind('<Button-1>', self._on_drag_start)
        title_lbl.bind('<B1-Motion>', self._on_drag)

        frame = tk.Frame(outer, bg='#2b2b2b', padx=10, pady=10)
        frame.pack()

        params = self.shape.get_params()
        row = 0
        for key, label, kind in PARAM_LABELS:
            if key not in params:
                continue

            tk.Label(
                frame, text=label, bg='#2b2b2b', fg='#ccc',
                font=('Segoe UI', 9), anchor='w',
            ).grid(row=row, column=0, sticky='w', pady=3, padx=(0, 8))

            if kind == 'color':
                var = tk.StringVar(value=str(params[key]))
                self._vars[key] = var
                color_frame = tk.Frame(frame, bg='#2b2b2b')
                color_frame.grid(row=row, column=1, sticky='ew', pady=3)
                preview = tk.Label(color_frame, bg=params[key], width=3)
                preview.pack(side='left', padx=(0, 4))
                self._color_previews[key] = preview
                tk.Button(
                    color_frame, text='選択', relief='flat',
                    bg='#555', fg='white', padx=4, pady=1,
                    command=lambda k=key, p=preview: self._pick_color(k, p),
                    cursor='hand2',
                ).pack(side='left')
            else:
                var = tk.StringVar(value=str(params[key]))
                self._vars[key] = var
                entry = tk.Entry(
                    frame, textvariable=var, width=10,
                    bg='#3c3c3c', fg='white', insertbackground='white',
                    relief='flat', bd=4,
                )
                entry.grid(row=row, column=1, sticky='ew', pady=3)
                var.trace_add('write', lambda *_, k=key, v=var, t=kind: self._on_change(k, v, t))

            row += 1

    def refresh(self) -> None:
        """ハンドル操作など外部からの図形変更をウィンドウに反映する。"""
        self._refreshing = True
        params = self.shape.get_params()
        for key, var in self._vars.items():
            value = params.get(key)
            if value is None:
                continue
            if isinstance(value, float):
                new_val = f'{value:.1f}'
            else:
                new_val = str(value)
            if var.get() != new_val:
                var.set(new_val)
        # カラープレビューも更新
        for key, preview in self._color_previews.items():
            color = params.get(key)
            if color:
                preview.config(bg=color)
        self._refreshing = False

    def _on_change(self, key: str, var: tk.StringVar, kind: str):
        if self._refreshing:
            return
        try:
            val = var.get()
            if kind == 'float':
                setattr(self.shape, key, float(val))
            elif kind == 'int':
                setattr(self.shape, key, int(val))
            self.on_change()
        except ValueError:
            pass

    def _pick_color(self, key: str, preview: tk.Label):
        current = getattr(self.shape, key, 'red')
        result = colorchooser.askcolor(color=current, title='色を選択')
        if result and result[1]:
            color = result[1]
            setattr(self.shape, key, color)
            preview.config(bg=color)
            if key in self._vars:
                self._vars[key].set(color)
            self.on_change()

    def _on_drag_start(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.win.winfo_x() + event.x - self._drag_x
        y = self.win.winfo_y() + event.y - self._drag_y
        self.win.geometry(f'+{x}+{y}')
