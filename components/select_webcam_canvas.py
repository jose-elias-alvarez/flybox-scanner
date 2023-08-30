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

        # on macOS, at least, indeterminate mode doesn't seem to work
        self.button_frame = tk.Frame(self.window)
        self.progress = ttk.Progressbar(self.button_frame, mode="indeterminate")
        self.select_button = tk.Button(
            self.button_frame, text="Select", command=self.window.state_manager.idle
        )
        self.dropdown = None  # easier to create this later

    def layout(self):
        super().grid()
        self.button_frame.grid(row=1, column=0, sticky="ew")
        self.progress.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.progress.start()

    def check_thread(self):
        if self.thread.is_alive():
            self.window.after(self.check_interval, self.check_thread)
        else:
            self.progress.stop()
            self.progress.grid_forget()

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

        self.window.after_idle(self.update_dropdown)

    def update_dropdown(self):
        self.dropdown = tk.OptionMenu(
            self.button_frame,
            self.selected_source,
            *["Webcam " + str(i + 1) for i in self.sources],
            command=self.change_webcam,
        )
        self.button_frame.grid_configure(sticky="")
        self.dropdown.grid(row=0, column=0)
        self.select_button.grid(row=0, column=1)

    def change_webcam(self, selected_source: str):
        self.current_source = int(selected_source.split(" ")[1]) - 1
        self.window.set_cap(cv2.VideoCapture(self.current_source))

    def on_close(self):
        self.thread.join()
