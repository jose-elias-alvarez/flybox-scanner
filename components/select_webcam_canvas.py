import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

import cv2

from components.frame_canvas import FrameCanvas

if TYPE_CHECKING:
    from components.root_window import RootWindow


class SelectWebcamCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)
        self.window.cleanup.put(self.on_close)

        self.thread = threading.Thread(target=self.get_webcams)
        self.thread.start()

        # update every 100ms
        self.check_interval = 100
        self.check_thread()

        self.sources = [0]
        self.current_source = self.sources[0]
        self.window.set_cap(cv2.VideoCapture(self.current_source))
        self.selected_source = tk.StringVar()
        self.selected_source.set("Webcam 1")

        # on macOS, indeterminate mode doesn't seem to work
        self.progress = ttk.Progressbar(window, mode="indeterminate")
        self.dropdown = None
        self.select_button = tk.Button(
            self.window, text="Select", command=self.window.state_manager.idle
        )

    def pack(self):
        super().pack()
        self.progress.pack(fill=tk.BOTH, expand=True)
        self.progress.start()

    def check_thread(self):
        if self.thread.is_alive():
            self.window.after(self.check_interval, self.check_thread)
        else:
            self.progress.stop()
            self.progress.pack_forget()

    def get_webcams(self):
        index = 1
        while index < 10:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                self.sources.append(index)
            cap.release()
            index += 1

        if len(self.sources) == 1:
            messagebox.showinfo("Select Webcam", "Only 1 webcam found!")
            self.window.after_idle(self.window.state_manager.idle)
        else:
            self.window.after_idle(self.update_dropdown)

    def update_dropdown(self):
        self.dropdown = tk.OptionMenu(
            self.window,
            self.selected_source,
            *["Webcam " + str(i + 1) for i in self.sources],
            command=self.change_webcam,
        )
        self.dropdown.pack()
        self.select_button.pack()

    def change_webcam(self, selected_source: str):
        self.current_source = int(selected_source.split(" ")[1]) - 1
        self.window.set_cap(cv2.VideoCapture(self.current_source))

    def on_close(self):
        self.thread.join()
