import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.capture_canvas import CaptureCanvas


class HideButton(tk.Button):
    def __init__(self, window, canvas: "CaptureCanvas"):
        super().__init__(window, text="Hide", command=self.hide_frame)
        self.canvas = canvas
        self.window = window

    def hide_frame(self):
        self.canvas.hidden = not self.canvas.hidden
        self.config(text="Show" if self.canvas.hidden else "Hide")
