import tkinter as tk
from typing import TYPE_CHECKING

from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler

if TYPE_CHECKING:
    from components.main_window import MainWindow


class AcceptButton(tk.Button):
    def __init__(self, window: "MainWindow"):
        super().__init__(window, text="Accept", command=self.accept_frame)
        self.window = window

    def accept_frame(self):
        to_file_handler = ToFileHandler(self.window.grid)
        resolution_handler = ResolutionHandler(5, to_file_handler)
        resolution_handler.start()

        def wrapped_handler(e):
            resolution_handler.handle(e)
            debug_handler(e)

        self.window.frame_handler = FrameHandler(self.window.grid, wrapped_handler)
        self.window.paused = False

        self.pack_forget()
        self.window.capture_button.pack_forget()
        self.window.hide_button.pack()
