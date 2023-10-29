import tkinter as tk
from os import getcwd, path
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
        self.filename = None
        self.output_path = None

        try:
            grid = window.app_state["grid"]
        except KeyError:
            raise Exception("Grid not initialized")

        if window.tuning_mode == "motion":
            handler = MotionEventHandler()
        else:
            self.filename = self.window.settings.get(
                "recording.output_file"
            ) or filedialog.asksaveasfilename(defaultextension=".txt")
            if self.filename == "":
                raise ValueError("No output file selected")
            handler = FileIntervalHandler(
                grid,
                self.filename,
                cleanup_queue=window.cleanup,
                error_queue=window.errors,
                interval=window.settings.get("recording.interval"),
            )
            handler.start()
        wrapped_handler = DebugHandler(grid, handler, lambda: not self.hidden)
        self.frame_handler = FrameHandler(grid, window.settings, wrapped_handler)

        self.frame = tk.Frame(self.window)
        self.path_label = None
        self.hide_button = None
        self.stop_button = tk.Button(
            self.frame, text="Stop", command=self.window.state_manager.idle
        )
        if self.filename is not None:
            if self.filename.startswith(getcwd()):
                self.output_path = path.relpath(self.filename)
            else:
                self.output_path = self.filename
            self.path_label = tk.Label(self.frame, text=f"Output: {self.output_path}")
            self.hide_button = tk.Button(
                self.frame, text="Hide", command=self.toggle_hide
            )

        self.hidden_frame = tk.Frame(self.window)
        tk.Label(self.hidden_frame, text="Hidden").grid()

        self.tuning_frame = None
        if self.window.tuning_mode == "motion":
            self.tuning_frame = TuneMotionFrame(
                window, self.frame_handler.motion_detector
            )

    def layout(self):
        super().grid()
        self.frame.grid(row=1, column=0)
        if self.filename is not None:
            self.path_label.grid(row=0, column=0)
            self.hide_button.grid(row=0, column=1)
        self.stop_button.grid(row=0, column=2)
        if self.tuning_frame is not None:
            self.tuning_frame.layout()

    def toggle_hide(self):
        if self.hidden:
            self.hidden = False
            self.hide_button.config(text="Hide")
            self.config(width=self.window.width, height=self.window.height)
            self.hidden_frame.grid_forget()
        else:
            self.hidden = True
            self.hide_button.config(text="Show")
            self.config(width=0, height=0)
            # mount at window center
            self.hidden_frame.grid(row=0, column=0)

    def resize_frame(self, frame):
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
