import tkinter as tk
from tkinter import filedialog

import cv2

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
        self.select_video_button = tk.Button(
            window, text="Select Video", command=self.pick_video
        )

    def pack(self):
        super().pack()
        self.capture_button.pack()
        self.select_webcam_button.pack()
        self.select_video_button.pack()

    def pick_video(self):
        filename = filedialog.askopenfilename(
            filetypes=(("Video files", "*.mp4 *.avi"),)
        )
        if filename == "":
            return
        self.window.set_cap(cv2.VideoCapture(filename))
