import tkinter as tk

from components.frame_canvas import FrameCanvas


class IdleCanvas(FrameCanvas):
    def __init__(self, window):
        super().__init__(window)

        self.capture_button = tk.Button(
            window, text="Capture", command=window.state_manager.capture
        )
        self.select_webcam_button = tk.Button(
            window, text="Select Webcam", command=window.state_manager.select_webcam
        )

    def pack(self):
        super().pack()
        self.capture_button.pack()
        self.select_webcam_button.pack()
