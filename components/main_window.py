import tkinter as tk

import cv2
from PIL import Image, ImageTk

from components.accept_button import AcceptButton
from components.capture_button import CaptureButton
from components.hide_button import HideButton
from detection.border import BorderDetector

MAX_WIDTH = 640
MAX_HEIGHT = 480


class MainWindow(tk.Tk):
    def __init__(self, cap):
        super().__init__()
        self.paused = False
        self.hidden = False
        self.image = None
        self.image_id = None
        self.grid = None
        self.frame_handler = None

        self.cap = cap
        self.frame_count = 0
        self.border_detector = BorderDetector()

        first_frame = self.get_frame()[0]
        self.width = first_frame.shape[1]
        self.height = first_frame.shape[0]

        self.title = "Webcam Capture"
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        # visible elements
        self.capture_button = CaptureButton(self)
        self.capture_button.pack()
        # hidden elements
        self.hide_button = HideButton(self)
        self.accept_button = AcceptButton(self)

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
        if (MAX_WIDTH / aspect_ratio) > MAX_HEIGHT:
            new_width = int(MAX_HEIGHT * aspect_ratio)
            new_height = MAX_HEIGHT
        else:
            new_height = int(MAX_WIDTH / aspect_ratio)
            new_width = MAX_WIDTH

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
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def delete_frame(self):
        if self.image_id is None:
            return
        self.canvas.delete(self.image_id)
        self.image_id = None

    def schedule_update(self):
        self.after(33, self.update)

    def update(self):
        if self.paused:
            self.schedule_update()
            return

        frame, frame_count = self.get_frame()
        self.handle_frame(frame, frame_count)
        if self.hidden:
            self.delete_frame()
        else:
            self.show_frame(frame)
        self.schedule_update()

    def start(self):
        self.update()
        self.mainloop()
