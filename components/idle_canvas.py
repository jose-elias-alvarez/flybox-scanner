import tkinter as tk
from tkinter import filedialog
from typing import TYPE_CHECKING

from components.frame_canvas import FrameCanvas

if TYPE_CHECKING:
    from components.root_window import RootWindow


class IdleCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)

        self.button_frame = tk.Frame(self.window)
        self.scan_button = tk.Button(
            self.button_frame, text="Scan", command=window.state_manager.scan
        )
        self.select_webcam_button = tk.Button(
            self.button_frame,
            text="Select Webcam",
            command=window.state_manager.select_webcam,
        )
        self.select_video_button = tk.Button(
            self.button_frame, text="Select Video", command=self.pick_video
        )

    def layout(self):
        super().grid()
        self.button_frame.grid(row=1, column=0)
        self.scan_button.grid(row=0, column=0)
        self.select_webcam_button.grid(row=0, column=1)
        self.select_video_button.grid(row=0, column=2)

    def pick_video(self):
        filename = filedialog.askopenfilename(
            filetypes=(("Video files", "*.mp4 *.avi"),)
        )
        if filename == "":
            return
        self.window.set_source(filename)
