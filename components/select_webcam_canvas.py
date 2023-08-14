import tkinter as tk
from typing import TYPE_CHECKING

import cv2
import PIL.Image
import PIL.ImageTk

if TYPE_CHECKING:
    from components.root_window import RootWindow


class SelectWebcamCanvas(tk.Canvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window, width=window.width, height=window.height)
        self.pack()
        self.window = window

        self.sources = self.get_webcams()
        self.current_source = self.sources[0]
        self.cap = cv2.VideoCapture(self.current_source)
        self.frame = None

        self.selected_source = tk.StringVar()
        self.selected_source.set("Webcam 1")  # initial value
        self.dropdown = tk.OptionMenu(
            self.window,
            self.selected_source,
            *["Webcam " + str(i + 1) for i in self.sources],
            command=self.change_webcam
        )
        self.dropdown.pack()

        self.select_button = tk.Button(self.window, text="Select", command=self.select)
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
        print(selected_source)
        self.current_source = int(selected_source.split(" ")[1]) - 1
        self.cap.release()
        self.cap = cv2.VideoCapture(self.current_source)

    def resize(self, image):
        (h, w) = image.shape[:2]
        r = self.window.width / float(w)
        dim = (self.window.width, int(h * r))

        return cv2.resize(image, dim)

    def select(self):
        self.window.cap = self.cap
        self.window.on_idle()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.resize(frame)
            self.frame = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            )
            self.create_image(0, 0, image=self.frame, anchor=tk.NW)
