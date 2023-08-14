import tkinter as tk
from enum import Enum

import cv2

from components.capture_button import CaptureButton
from components.hide_button import HideButton
from components.main_canvas import MainCanvas
from components.record_button import RecordButton
from components.select_webcam_canvas import SelectWebcamCanvas


class RootState(Enum):
    IDLE = "Idle"
    CAPTURING = "Capturing"
    RECORDING = "Recording"
    SELECTING_WEBCAM = "Selecting Webcam"


class CommandButton(tk.Button):
    def __init__(self, window: "RootWindow", text: str, command):
        super().__init__(window, text=text, command=command)


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

        self._cap = cv2.VideoCapture(0)
        self.on_idle()

    # setter for cap that releases the previous cap
    @property
    def cap(self):
        return self._cap

    @cap.setter
    def cap(self, cap):
        if self._cap is not None:
            self._cap.release()
        self._cap = cap

    def wipe(self):
        if self.canvas is not None:
            self.canvas.destroy()
        for component in self.winfo_children():
            component.destroy()

    def on_idle(self):
        self.wipe()
        self.canvas = MainCanvas(self, self.cap)
        self.canvas.pack()
        # visible elements
        self.capture_button = CaptureButton(self, self.canvas)
        self.capture_button.pack()
        self.select_webcam_button = CommandButton(
            self, "Select Webcam", self.on_selecting_webcam
        )
        self.select_webcam_button.pack()
        # hidden elements
        self.hide_button = HideButton(self, self.canvas)
        self.record_button = RecordButton(self, self.canvas)
        self.cancel_button = CommandButton(self, "Cancel", self.on_idle)

        self.state = RootState.IDLE

    def on_capturing(self):
        self.capture_button.config(text="Retry")
        self.record_button.pack()
        self.cancel_button.pack()
        self.select_webcam_button.pack_forget()
        self.state = RootState.CAPTURING

    def on_recording(self):
        self.capture_button.pack_forget()
        self.record_button.pack_forget()
        self.hide_button.pack()
        self.state = RootState.RECORDING

    def on_selecting_webcam(self):
        self.wipe()
        self.canvas = SelectWebcamCanvas(self)
        self.state = RootState.SELECTING_WEBCAM

    def schedule_update(self):
        self.after(self.delay, self.update)

    def update(self):
        self.canvas.update()
        self.schedule_update()

    def start(self):
        self.update()
        self.mainloop()
