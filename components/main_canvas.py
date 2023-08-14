import tkinter as tk

import cv2
from PIL import Image, ImageTk

from detection.border import BorderDetector


class MainCanvas(tk.Canvas):
    def __init__(self, window, cap):
        super().__init__(width=window.width, height=window.height)
        self.window = window
        self.cap = cap
        self.frame_count = 0
        self.border_detector = BorderDetector()

        self.paused = False
        self.hidden = False
        self.image = None
        self.image_id = None
        self.grid = None
        self.frame_handler = None

        first_frame = self.get_frame()[0]
        self.width = first_frame.shape[1]
        self.height = first_frame.shape[0]

    def get_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            raise Exception("Could not read frame")
        frame = self.resize_frame(frame)
        self.frame_count += 1
        return frame, self.frame_count

    def resize_frame(self, frame):
        (x, y, w, h) = self.border_detector.get_border(frame)
        frame = frame[y : y + h, x : x + w]

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

    def handle_frame(self, frame, frame_count):
        if self.frame_handler is None:
            return

        self.frame_handler.handle(frame, frame_count)

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

    def update(self):
        if self.paused:
            return

        frame, frame_count = self.get_frame()
        self.handle_frame(frame, frame_count)
        if self.hidden:
            self.delete_frame()
        else:
            self.show_frame(frame)
