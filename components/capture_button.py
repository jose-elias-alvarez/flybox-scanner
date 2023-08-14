import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

import cv2

from detection.grids import GridDetector

if TYPE_CHECKING:
    from components.main_canvas import MainCanvas
    from components.root_window import RootWindow


class CaptureButton(tk.Button):
    def __init__(self, window: "RootWindow", canvas: "MainCanvas"):
        super().__init__(window, text="Capture", command=self.capture_frame)
        self.window = window
        self.canvas = canvas

    def capture_frame(self):
        self.canvas.paused = True
        frame = self.canvas.get_frame()[0]
        grid_detector = GridDetector(frame)
        try:
            self.canvas.grid = grid_detector.detect()
        except Exception as e:
            messagebox.showwarning("Detection Failed", str(e))
            self.canvas.paused = False
            return

        # draw grid on frame
        for row in self.canvas.grid.rows:
            for item in row.items:
                cv2.rectangle(
                    frame,
                    (int(item.start_point[0]), int(item.start_point[1])),
                    (int(item.end_point[0]), int(item.end_point[1])),
                    (0, 255, 0),
                    thickness=1,
                )
        # also draw number of rows and columns
        cv2.putText(
            frame,
            f"{len(self.canvas.grid.rows)}x{len(self.canvas.grid.rows[0].items)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            thickness=2,
        )

        self.canvas.show_frame(frame)
        self.window.on_capturing()
