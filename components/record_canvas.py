import tkinter as tk

from components.frame_canvas import FrameCanvas
from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler


class RecordCanvas(FrameCanvas):
    def __init__(self, window, capture_canvas):
        super().__init__(window)
        self.hidden = False
        self.border_detector = capture_canvas.border_detector

        grid = capture_canvas.grid
        to_file_handler = ToFileHandler(grid)
        resolution_handler = ResolutionHandler(5, to_file_handler, window.errors)
        resolution_handler.start()
        # make sure cancel() is called on unmount
        self.window.cleanup.put(resolution_handler.cancel)

        def wrapped_handler(e):
            resolution_handler.handle(e)
            debug_handler(e)

        self.frame_handler = FrameHandler(grid, wrapped_handler)

        self.stop_button = tk.Button(
            text="Stop", command=self.window.state_manager.idle
        )
        self.hide_button = tk.Button(text="Hide", command=self.toggle_hide)

    def pack(self):
        super().pack()
        self.hide_button.pack()
        self.stop_button.pack()

    def toggle_hide(self):
        self.hidden = not self.hidden
        self.hide_button.config(text="Show" if self.hidden else "Hide")

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
