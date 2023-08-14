import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.root_window import RootWindow


class CancelButton(tk.Button):
    def __init__(self, window: "RootWindow"):
        super().__init__(window, text="Cancel", command=window.on_idle)
        self.window = window
