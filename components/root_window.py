import tkinter as tk
from enum import Enum

import cv2

from components.cancel_button import CancelButton
from components.capture_button import CaptureButton
from components.hide_button import HideButton
from components.main_canvas import MainCanvas
from components.record_button import RecordButton


class RootState(Enum):
    IDLE = "Idle"
    CAPTURING = "Capturing"
    RECORDING = "Recording"


class RootWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title = "Flybox Scanner"
        self.width = 640
        self.height = 480
        self.delay = 33

        self.canvas = None
        self.capture_button = None
        self.hide_button = None
        self.record_button = None
        self.cancel_button = None

        self.cap = cv2.VideoCapture(0)

        self.on_idle()

    def on_idle(self):
        if self.canvas is not None:
            self.canvas.destroy()
        for component in self.winfo_children():
            component.destroy()

        self.canvas = MainCanvas(self, self.cap)
        self.canvas.pack()
        # visible elements
        self.capture_button = CaptureButton(self, self.canvas)
        self.capture_button.pack()
        # hidden elements
        self.hide_button = HideButton(self, self.canvas)
        self.record_button = RecordButton(self, self.canvas)
        self.cancel_button = CancelButton(self)

        self.state = RootState.IDLE

    def on_capturing(self):
        self.capture_button.config(text="Retry")
        self.record_button.pack()
        self.cancel_button.pack()
        self.state = RootState.CAPTURING

    def on_recording(self):
        self.capture_button.pack_forget()
        self.record_button.pack_forget()
        self.hide_button.pack()
        self.state = RootState.RECORDING

    def schedule_update(self):
        self.after(self.delay, self.update)

    def update(self):
        self.canvas.update()
        self.schedule_update()

    def start(self):
        self.update()
        self.mainloop()
