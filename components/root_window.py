import queue
import tkinter as tk
import traceback
from os import environ
from tkinter import messagebox
from typing import Any, Callable

import cv2

from components.state_canvas import StateCanvas
from components.state_manager import StateManager
from utils.app_settings import AppSettings
from utils.arg_parser import arg_parser


class RootWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.cap = None
        self.set_source(self.settings.get("video.source"))
        self.frame_delay = self.settings.get("video.frame_delay")

        self.args = arg_parser()
        self.tuning_mode = self.args.tuning

        self.title(self.settings.get("window.title"))
        self.width = self.settings.get("window.width")
        self.height = self.settings.get("window.height")
        if self.settings.get("window.resizable") is False:
            self.resizable(False, False)

        self.is_running = True
        # this handles closing via the close button
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # and this handles command-q on macOS
        menubar = tk.Menu(self)
        mac_app_menu = tk.Menu(menubar, name="apple")
        menubar.add_cascade(menu=mac_app_menu)
        self.createcommand("tk::mac::Quit", self.on_close)

        # queue of callbacks to run on wipe
        self.cleanup: queue.SimpleQueue[Callable[[], None]] = queue.SimpleQueue()
        # queue of errors from threads
        self.errors: queue.SimpleQueue[Exception] = queue.SimpleQueue()

        # dictionary of arbitrary values to share between components
        self.app_state: dict[str, Any] = {}

        self.canvas: StateCanvas | None = None
        self.state_manager = StateManager(self)
        if environ.get("OUTPUT_FILE"):
            self.state_manager.scan()
        else:
            self.state_manager.idle()

        # override default error handling
        self.report_callback_exception = self.handle_exception
        self.after_id: str | None = None

    def on_close(self):
        while not self.cleanup.empty():
            callback = self.cleanup.get()
            callback()
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.is_running = False
        self.destroy()

    def wipe(self):
        while not self.cleanup.empty():
            callback = self.cleanup.get()
            callback()
        for component in self.winfo_children():
            if component != self.canvas:
                component.destroy()
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None

    def set_source(self, source: str | int):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cap = cv2.VideoCapture()
        cap.open(source)
        if not cap.isOpened():
            raise IOError(f"Unable to open video source: {source}")
        self.cap = cap

    # because tkinter elements are tied to a window on creation,
    # we use a factory function to create the canvas
    def set_canvas(self, canvas_factory: Callable[[], StateCanvas]):
        self.wipe()
        self.canvas = canvas_factory()
        self.canvas.layout()

    def schedule_update(self):
        self.after_id = self.after(self.frame_delay, self.update)

    def update(self):
        # on each iteration, we check for errors from threads
        try:
            error = self.errors.get_nowait()
            raise error
        except queue.Empty:
            pass

        if not self.is_running:
            return
        if self.canvas is not None:
            self.canvas.update()
        self.schedule_update()

    def start(self):
        self.update()
        self.mainloop()

    def handle_exception(self, exctype, value, trace):
        # TODO: add file logging
        traceback.print_exception(exctype, value, trace)
        # for now, show message box and quit, since these are unhandled
        messagebox.showerror("Error", value)
        self.on_close()
        self.quit()
