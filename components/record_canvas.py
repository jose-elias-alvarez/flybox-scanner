import tkinter as tk

from components.frame_canvas import FrameCanvas
from components.hide_button import HideButton
from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler


class RecordCanvas(FrameCanvas):
    def __init__(self, window, cap, grid, border_detector):
        super().__init__(window, cap)

        self.hidden = False
        self.grid = grid
        self.border_detector = border_detector

        to_file_handler = ToFileHandler(self.grid)
        resolution_handler = ResolutionHandler(5, to_file_handler, window.errors)
        resolution_handler.start()
        # make sure cancel() is called on unmount
        self.window.cleanup.put(resolution_handler.cancel)

        def wrapped_handler(e):
            resolution_handler.handle(e)
            debug_handler(e)

        self.frame_handler = FrameHandler(self.grid, wrapped_handler)

        self.hide_button = HideButton(self.window, self)
        self.stop_button = tk.Button(text="Stop", command=self.window.on_idle)

    def pack(self):
        super().pack()
        self.hide_button.pack()
        self.stop_button.pack()

    def resize_frame(self, frame):
        (x, y, w, h) = self.border_detector.get_border(frame)
        frame = frame[y : y + h, x : x + w]

        return super().resize_frame(frame)

    def update(self):
        frame, frame_count = self.get_frame()
        self.frame_handler.handle(frame, frame_count)
        if self.hidden:
            self.delete_frame()
        else:
            self.show_frame(frame)
