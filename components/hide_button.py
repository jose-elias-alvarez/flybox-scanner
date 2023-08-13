import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.main_window import MainWindow


class HideButton(tk.Button):
    def __init__(self, window: "MainWindow"):
        super().__init__(window, text="Hide", command=self.hide_frame)
        self.window = window

    def hide_frame(self):
        self.window.hidden = not self.window.hidden
        self.config(text="Show" if self.window.hidden else "Hide")
