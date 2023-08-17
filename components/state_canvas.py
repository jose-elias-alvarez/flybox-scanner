import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.root_window import RootWindow


class StateCanvas(tk.Canvas):
    def __init__(self, window: "RootWindow", **kwargs):
        super().__init__(width=window.width, height=window.height, **kwargs)
        self.window = window

    def layout(self):
        # assume that all instances have a layout for now
        raise NotImplementedError

    def update(self):
        pass
