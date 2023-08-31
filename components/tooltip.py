import tkinter as tk


class Tooltip:
    def __init__(self, parent: tk.Widget, text: str, **kwargs):
        self.parent = parent
        self.text = text
        self.wait_time = kwargs.get("wait_time", 500)
        self.wrap_length = kwargs.get("wrap_length", 180)
        self.background = kwargs.get("background", "#FFFFEA")
        self.offset = kwargs.get("offset", (25, 20))

        self.parent.bind("<Enter>", self.on_enter)
        self.parent.bind("<Leave>", self.on_leave)
        self.tw = None
        self.id = None

    def on_enter(self, _):
        self.id = self.parent.after(self.wait_time, self.show_tip)

    def on_leave(self, _):
        if self.id is not None:
            self.parent.after_cancel(self.id)
        self.hide_tip()

    def show_tip(self):
        x, y, _, _ = self.parent.bbox("insert")
        (x_offset, y_offset) = self.offset
        x += self.parent.winfo_rootx() + x_offset
        y += self.parent.winfo_rooty() + y_offset
        self.tw = tk.Toplevel(self.parent)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tw,
            text=self.text,
            wraplength=self.wrap_length,
            background=self.background,
        )
        label.pack()

    def hide_tip(self):
        if self.tw is not None:
            self.tw.destroy()
