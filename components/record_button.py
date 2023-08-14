import tkinter as tk
from typing import TYPE_CHECKING

from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler

if TYPE_CHECKING:
    from components.main_canvas import MainCanvas
    from components.root_window import RootWindow


class RecordButton(tk.Button):
    def __init__(self, window: "RootWindow", canvas: "MainCanvas"):
        super().__init__(window, text="Record", command=self.accept_frame)
        self.window = window
        self.canvas = canvas

    def accept_frame(self):
        to_file_handler = ToFileHandler(self.canvas.grid)
        resolution_handler = ResolutionHandler(5, to_file_handler)
        resolution_handler.start()

        def wrapped_handler(e):
            resolution_handler.handle(e)
            debug_handler(e)

        self.canvas.frame_handler = FrameHandler(self.canvas.grid, wrapped_handler)
        self.canvas.paused = False

        self.window.on_recording()
