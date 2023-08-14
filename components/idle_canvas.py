import tkinter as tk
from tkinter import filedialog
from typing import TYPE_CHECKING

import cv2

from components.frame_canvas import FrameCanvas

if TYPE_CHECKING:
    from components.root_window import RootWindow


class IdleCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)

        self.scan_button = tk.Button(
            window, text="Scan", command=window.state_manager.scan
        )
        self.select_webcam_button = tk.Button(
            window, text="Select Webcam", command=window.state_manager.select_webcam
        )
        self.select_video_button = tk.Button(
            window, text="Select Video", command=self.pick_video
        )

    def pack(self):
        super().pack()
        self.scan_button.pack()
        self.select_webcam_button.pack()
        self.select_video_button.pack()

    def pick_video(self):
        filename = filedialog.askopenfilename(
            filetypes=(("Video files", "*.mp4 *.avi"),)
        )
        if filename == "":
            return
        self.window.set_cap(cv2.VideoCapture(filename))
