import tkinter as tk
from os import environ
from tkinter import filedialog
from typing import TYPE_CHECKING

from components.frame_canvas import FrameCanvas
from components.tuning.motion import TuneMotionFrame
from custom_types.motion import MotionEventHandler
from handlers.debug import DebugHandler
from handlers.file_interval import FileIntervalHandler
from handlers.frame import FrameHandler

if TYPE_CHECKING:
    from components.root_window import RootWindow


class RecordCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)
        self.hidden = False

        if window.tuning_mode == "motion":
            handler = MotionEventHandler()
        else:
            try:
                filename = environ["OUTPUT_FILE"]
            except KeyError:
                filename = filedialog.asksaveasfilename(defaultextension=".txt")
            handler = FileIntervalHandler(window, filename)
            handler.start()

        wrapped_handler = DebugHandler(handler)
        self.frame_handler = FrameHandler(window, wrapped_handler)

        self.button_frame = tk.Frame(self.window)
        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.window.state_manager.idle
        )
        self.hide_button = tk.Button(
            self.button_frame, text="Hide", command=self.toggle_hide
        )

        self.tuning_frame = None
        if self.window.tuning_mode == "motion":
            self.tuning_frame = TuneMotionFrame(
                window, self.frame_handler.motion_detector
            )

    def layout(self):
        super().grid()
        self.button_frame.grid(row=1, column=0)
        self.hide_button.grid(row=0, column=0)
        self.stop_button.grid(row=0, column=1)
        if self.tuning_frame is not None:
            self.tuning_frame.layout()

    def toggle_hide(self):
        if self.hidden:
            self.hidden = False
            self.hide_button.config(text="Hide")
            self.config(width=self.window.width, height=self.window.height)
        else:
            self.hidden = True
            self.hide_button.config(text="Show")
            self.config(width=0, height=0)

    def resize_frame(self, frame):
        # don't resize if hidden to avoid messing up canvas size
        if self.hidden:
            return frame

        try:
            border = self.window.app_state["border"]
            (x, y, w, h) = border
            frame = frame[y : y + h, x : x + w]
        except KeyError:
            pass

        return super().resize_frame(frame)

    def update(self):
        frame, frame_count = self.get_frame()
        self.frame_handler.handle(frame, frame_count)
        if self.hidden:
            self.delete_frame()
        else:
            self.show_frame(frame)
