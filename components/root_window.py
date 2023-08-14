import queue
import tkinter as tk
from enum import Enum
from tkinter import messagebox

from components.capture_canvas import CaptureCanvas
from components.frame_canvas import FrameCanvas
from components.record_canvas import RecordCanvas
from components.select_webcam_canvas import SelectWebcamCanvas


class RootState(Enum):
    IDLE = "Idle"
    CAPTURING = "Capturing"
    SELECTING_WEBCAM = "Selecting Webcam"
    RECORDING = "Recording"


class RootWindow(tk.Tk):
    def __init__(self, cap):
        super().__init__()
        self.report_callback_exception = self.handle_exception

        self.title = "Flybox Scanner"
        self.width = 640
        self.height = 480
        self.delay = 33
        # queue of cleanup callbacks to run on wipe
        self.cleanup = queue.SimpleQueue()
        # queue of errors from threads
        self.errors = queue.SimpleQueue()

        self.canvas: FrameCanvas | None = None
        self.capture_button: tk.Button | None = None
        self.select_webcam_button: tk.Button | None = None

        self.cap = cap
        self.on_idle()

    def wipe(self):
        # drain cleanup queue
        while not self.cleanup.empty():
            callback = self.cleanup.get()
            callback()

        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None
        for component in self.winfo_children():
            component.destroy()

    def set_cap(self, cap):
        if self.cap is not None:
            self.cap.release()
        self.cap = cap

    def on_idle(self):
        self.wipe()

        self.canvas = FrameCanvas(self, self.cap)
        self.canvas.pack()

        self.capture_button = tk.Button(self, text="Capture", command=self.on_capturing)
        self.select_webcam_button = tk.Button(
            self, text="Select Webcam", command=self.on_selecting_webcam
        )
        self.capture_button.pack()
        self.select_webcam_button.pack()

        self.state = RootState.IDLE

    def on_capturing(self):
        self.wipe()

        self.canvas = CaptureCanvas(self, self.cap)
        self.canvas.pack()

        self.state = RootState.CAPTURING

    def on_selecting_webcam(self):
        self.wipe()

        self.canvas = SelectWebcamCanvas(self)
        self.canvas.pack()

        self.state = RootState.SELECTING_WEBCAM

    def on_recording(self):
        canvas = self.canvas
        if not isinstance(canvas, CaptureCanvas):
            raise Exception("Cannot record without a CaptureCanvas")
        if canvas.grid is None:
            raise Exception("Cannot record without a grid")

        self.wipe()
        # special case: we want to reuse these properties in the RecordCanvas
        # there's probably a better way to do this
        grid = canvas.grid
        border_detector = canvas.border_detector
        self.canvas = RecordCanvas(self, self.cap, grid, border_detector)
        self.canvas.pack()

        self.state = RootState.RECORDING

    def schedule_update(self):
        self.after(self.delay, self.update)

    def update(self):
        # check for errors from threads
        try:
            error = self.errors.get_nowait()
            raise error
        except queue.Empty:
            pass

        if self.canvas is not None:
            self.canvas.update()
        self.schedule_update()

    def start(self):
        self.update()
        self.mainloop()

    def handle_exception(self, exctype, value, traceback):
        # TODO: add logging
        # for now, show message box and quit, since these are unhandled
        messagebox.showerror("Error", value)
        self.quit()
