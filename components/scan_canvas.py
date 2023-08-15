import tkinter as tk
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import cv2

from components.frame_canvas import FrameCanvas
from detection.border import BorderDetector
from detection.grids import GridDetector

if TYPE_CHECKING:
    from components.root_window import RootWindow


class ScanCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)
        self.grid = None
        self.window.app_state.pop("grid", None)
        self.window.app_state.pop("border", None)

        self.hidden = False
        self.border_detector = BorderDetector()

        self.rescan_button = tk.Button(text="Rescan", command=self.detect_grid)

        def start_recording():
            # only set grid here now that it's confirmed
            self.window.app_state["grid"] = self.grid
            self.window.state_manager.record()

        self.record_button = tk.Button(text="Record", command=start_recording)
        # start disabled
        self.record_button.config(state=tk.DISABLED)
        self.cancel_button = tk.Button(
            text="Cancel", command=self.window.state_manager.idle
        )

        self.detect_grid()

    def pack(self):
        super().pack()
        self.rescan_button.pack()
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
            self.record_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showwarning("Detection Failed", str(e))

    def resize_frame(self, frame):
        try:
            (x, y, w, h) = self.window.app_state["border"]
        except KeyError:
            (x, y, w, h) = self.border_detector.get_border(frame)
            self.window.app_state["border"] = (x, y, w, h)
        frame = frame[y : y + h, x : x + w]
        return super().resize_frame(frame)

    def update(self):
        super().update()
