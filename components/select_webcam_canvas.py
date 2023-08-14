import tkinter as tk
from typing import TYPE_CHECKING

import cv2

from components.frame_canvas import FrameCanvas

if TYPE_CHECKING:
    from components.root_window import RootWindow


class SelectWebcamCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)
        self.sources = self.get_webcams()
        self.current_source = self.sources[0]
        self.window.set_cap(cv2.VideoCapture(self.current_source))

        self.selected_source = tk.StringVar()
        self.selected_source.set("Webcam 1")

        self.dropdown = tk.OptionMenu(
            self.window,
            self.selected_source,
            *["Webcam " + str(i + 1) for i in self.sources],
            command=self.change_webcam
        )
        self.select_button = tk.Button(
            self.window, text="Select", command=self.window.state_manager.idle
        )

    def pack(self):
        super().pack()
        self.dropdown.pack()
        self.select_button.pack()

    def get_webcams(self):
        index = 0
        arr = []
        while index < 10:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        return arr

    def change_webcam(self, selected_source):
        self.current_source = int(selected_source.split(" ")[1]) - 1
        self.window.set_cap(cv2.VideoCapture(self.current_source))

    def resize_frame(self, image):
        (h, w) = image.shape[:2]
        r = self.window.width / float(w)
        dim = (self.window.width, int(h * r))

        return cv2.resize(image, dim)
