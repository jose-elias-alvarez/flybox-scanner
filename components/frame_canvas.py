import tkinter as tk
from typing import TYPE_CHECKING

import cv2
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from components.root_window import RootWindow


class FrameCanvas(tk.Canvas):
    def __init__(self, window: "RootWindow", cap, **kwargs):
        super().__init__(width=window.width, height=window.height, **kwargs)
        self.window = window
        self.image_id = None
        self.image = None

        self.frame_count = 0
        self.cap = cap

    def resize_frame(self, frame):
        original_height, original_width = frame.shape[:2]
        aspect_ratio = original_width / original_height
        if (self.window.width / aspect_ratio) > self.window.height:
            new_width = int(self.window.height * aspect_ratio)
            new_height = self.window.height
        else:
            new_height = int(self.window.width / aspect_ratio)
            new_width = self.window.width

        frame = cv2.resize(frame, (new_width, new_height))
        return frame

    def get_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            raise Exception("Could not read frame")
        frame = self.resize_frame(frame)
        self.frame_count += 1
        return frame, self.frame_count

    def show_frame(self, frame):
        # fix colors
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        self.image = ImageTk.PhotoImage(pil_image)
        self.image_id = self.create_image(0, 0, anchor=tk.NW, image=self.image)

    def delete_frame(self):
        if self.image_id is None:
            return
        self.delete(self.image_id)
        self.image_id = None

    def on_init(self):
        pass

    def update(self):
        frame = self.get_frame()[0]
        self.show_frame(frame)
