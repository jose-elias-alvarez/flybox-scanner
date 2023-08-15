import queue
import tkinter as tk
import traceback
from tkinter import messagebox
from typing import Callable

from components.frame_canvas import FrameCanvas
from components.state_manager import StateManager


class RootWindow(tk.Tk):
    def __init__(self, cap):
        super().__init__()
        self.resizable(False, False)
        self.title("Flybox Scanner")

        self.cap = cap
        self.width = 640
        self.height = 480
        self.delay = 33
        self.is_running = True
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cleanup = queue.SimpleQueue()  # cleanup callbacks to run on wipe
        self.errors = queue.SimpleQueue()  # errors from threads

        # dictionary of arbitrary values to share between components
        self.app_state = {}

        self.state_manager = StateManager(self)
        self.canvas = None
        self.state_manager.idle()

        # override error handling
        self.report_callback_exception = self.handle_exception
        self.after_id = None

    def on_close(self):
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

    def set_cap(self, cap):
        if self.cap is not None:
            self.cap.release()
        self.cap = cap

    def set_canvas(self, canvas_factory: Callable[[], FrameCanvas]):
        # if we had passed in the canvas directly, it'd now get wiped, since it's a child of the root window
        self.wipe()
        self.canvas = canvas_factory()
        self.canvas.pack()
        self.canvas.transition()

    def schedule_update(self):
        self.after_id = self.after(self.delay, self.update)

    def update(self):
        # check for errors from threads
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
        self.quit()
