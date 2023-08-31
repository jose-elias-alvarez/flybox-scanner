import tkinter as tk
from typing import TYPE_CHECKING

from components.tooltip import Tooltip

if TYPE_CHECKING:
    from components import root_window
    from detection.motion import MotionDetector

LABELS = {
    "kernel_size": "Kernel",
    "should_blur": "Blur",
    "history": "History",
    "threshold": "Threshold",
}

TOOLTIPS = {
    "kernel_size": "Kernel size for morphological closing (larger = bigger objects)",
    "should_blur": "Blur the image before applying background subtraction. Reduces noise but erases small details.",
    "history": "Number of frames to use for background subtraction. Higher values require more motion to trigger a detection but take longer to react to camera / lighting changes.",
    "threshold": "Distance threshold for background subtraction. Higher values require more motion to trigger a detection.",
}


class TuneMotionFrame(tk.Frame):
    def __init__(self, window: "root_window", motion_detector: "MotionDetector"):
        super().__init__(window)
        self.window = window
        self.motion_detector = motion_detector
        for label in LABELS:
            if label in TOOLTIPS:
                LABELS[label] += " ℹ️"

        self.kernel_size_label = tk.Label(self, text=LABELS["kernel_size"], width=10)
        self.kernel_size_tooltip = Tooltip(
            self.kernel_size_label,
            TOOLTIPS["kernel_size"],
        )
        self.kernel_size_slider = tk.Scale(
            self,
            from_=1,
            to=24,
            orient=tk.HORIZONTAL,
            command=self.motion_detector.update_kernel_size,
        )
        self.kernel_size_slider.set(self.motion_detector.kernel_size)

        self.should_blur_checkbox = tk.Checkbutton(
            self,
            text=LABELS["should_blur"],
            command=self.motion_detector.toggle_should_blur,
        )
        self.should_blur_tooltip = Tooltip(
            self.should_blur_checkbox,
            TOOLTIPS["should_blur"],
        )
        if self.motion_detector.should_blur:
            self.should_blur_checkbox.select()
        self.blur_size_slider = tk.Scale(
            self,
            from_=1,
            to=24,
            orient=tk.HORIZONTAL,
            command=self.motion_detector.update_blur_size,
        )
        self.blur_size_slider.set(self.motion_detector.blur_size)

        self.history_label = tk.Label(self, text=LABELS["history"], width=10)
        self.history_tooltip = Tooltip(
            self.history_label,
            TOOLTIPS["history"],
        )
        self.history_slider = tk.Scale(
            self,
            from_=100,
            to=24000,
            orient=tk.HORIZONTAL,
            command=self.motion_detector.update_history,
        )
        self.history_slider.set(self.motion_detector.history)

        self.threshold_label = tk.Label(self, text=LABELS["threshold"], width=10)
        self.threshold_tooltip = Tooltip(
            self.threshold_label,
            TOOLTIPS["threshold"],
        )
        self.threshold_slider = tk.Scale(
            self,
            from_=10,
            to=600,
            orient=tk.HORIZONTAL,
            command=self.motion_detector.update_dist2_threshold,
        )
        self.threshold_slider.set(self.motion_detector.dist2_threshold)

    def layout(self):
        self.grid(row=2, column=0)
        self.kernel_size_label.grid(row=0, column=0)
        self.kernel_size_slider.grid(row=0, column=1)
        self.should_blur_checkbox.grid(row=0, column=2)
        self.blur_size_slider.grid(row=0, column=3)
        self.history_label.grid(row=1, column=0)
        self.history_slider.grid(row=1, column=1)
        self.threshold_label.grid(row=1, column=2)
        self.threshold_slider.grid(row=1, column=3)
