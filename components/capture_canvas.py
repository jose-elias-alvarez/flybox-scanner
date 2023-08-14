import tkinter as tk
from tkinter import messagebox

import cv2

from components.frame_canvas import FrameCanvas
from detection.border import BorderDetector
from detection.grids import GridDetector


class CaptureCanvas(FrameCanvas):
    def __init__(self, window, cap):
        super().__init__(window, cap)

        self.retry_button = tk.Button(text="Retry", command=self.detect_grid)
        self.record_button = tk.Button(text="Record", command=self.window.on_recording)
        self.cancel_button = tk.Button(text="Cancel", command=self.window.on_idle)

        self.border_detector = BorderDetector()

        self.grid = None
        self.hidden = False
        self.detect_grid()

    def pack(self):
        super().pack()
        self.retry_button.pack()
        self.record_button.pack()
        self.cancel_button.pack()

    def get_frame(self):
        frame, frame_count = super().get_frame()
        if self.grid is None:
            return frame, frame_count

        for row in self.grid.rows:
            for item in row.items:
                cv2.rectangle(
                    frame,
                    (int(item.start_point[0]), int(item.start_point[1])),
                    (int(item.end_point[0]), int(item.end_point[1])),
                    (0, 255, 0),
                    thickness=1,
                )
        cv2.putText(
            frame,
            f"{len(self.grid.rows)}x{len(self.grid.rows[0].items)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            thickness=2,
        )
        return frame, frame_count

    def detect_grid(self):
        frame = self.get_frame()[0]
        grid_detector = GridDetector(frame)
        try:
            self.grid = grid_detector.detect()
        except Exception as e:
            messagebox.showwarning("Detection Failed", str(e))

    def resize_frame(self, frame):
        (x, y, w, h) = self.border_detector.get_border(frame)
        frame = frame[y : y + h, x : x + w]

        return super().resize_frame(frame)

    def update(self):
        super().update()
