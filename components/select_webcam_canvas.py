import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from components.frame_canvas import FrameCanvas
from utils.get_webcams import get_webcams

if TYPE_CHECKING:
    from components.root_window import RootWindow


class SelectWebcamCanvas(FrameCanvas):
    def __init__(self, window: "RootWindow"):
        super().__init__(window)
        self.window.cleanup.put(self.on_close)

        self.thread = threading.Thread(target=self.get_webcams)
        self.thread.start()

        # update every 50ms
        self.check_interval = 50
        self.id = None
        self.check_thread()

        self.sources = [0]
        self.current_source = self.sources[0]
        self.selected_source = tk.StringVar()
        self.selected_source.set("Webcam " + str(self.current_source + 1))
        self.window.set_source(self.current_source)

        self.button_frame = tk.Frame(self.window)
        self.progress = ttk.Progressbar(self.button_frame, mode="indeterminate")
        self.select_button = tk.Button(
            self.button_frame, text="Select", command=self.window.state_manager.idle
        )
        self.dropdown = None  # easier to create this later

    def layout(self):
        super().grid()
        self.button_frame.grid(row=1, column=0, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.progress.grid(row=0, column=0, sticky="ew")
        self.progress.start()

    def check_thread(self):
        if self.thread.is_alive():
            self.id = self.window.after(self.check_interval, self.check_thread)
        else:
            self.progress.stop()
            self.progress.grid_forget()
            if self.id is not None:
                self.window.after_cancel(self.id)

    def get_webcams(self):
        self.sources = get_webcams()
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
        self.window.set_source(self.current_source)

    def on_close(self):
        self.thread.join()
