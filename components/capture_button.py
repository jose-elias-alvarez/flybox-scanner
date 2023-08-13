import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

import cv2

from detection.grids import GridDetector

if TYPE_CHECKING:
    from components.main_window import MainWindow


class CaptureButton(tk.Button):
    def __init__(self, window: "MainWindow"):
        super().__init__(window, text="Capture", command=self.capture_frame)
        self.window = window

    def capture_frame(self):
        self.window.paused = True
        frame = self.window.get_frame()[0]
        grid_detector = GridDetector(frame)
        try:
            self.window.grid = grid_detector.detect()
        except Exception as e:
            messagebox.showwarning("Detection Failed", str(e))
            self.window.paused = False
            return

        # draw grid on frame
        for row in self.window.grid.rows:
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
            f"{len(self.window.grid.rows)}x{len(self.window.grid.rows[0].items)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            thickness=2,
        )

        self.window.show_frame(frame)
        self.window.accept_button.pack()
