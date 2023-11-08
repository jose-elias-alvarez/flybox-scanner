import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.root_window import RootWindow
    from handlers.debug import DebugHandler


class DebugFrame(tk.Frame):
    def __init__(self, window: "RootWindow", handler: "DebugHandler"):
        super().__init__(window)
        self.window = window
        self.handler = handler

        self.draw_index = tk.BooleanVar()
        self.draw_index.set(self.handler.options.draw_index)
        self.draw_index_checkbox = tk.Checkbutton(
            self,
            text="Index",
            variable=self.draw_index,
            command=self.toggle_draw_index,
        )

        self.draw_fly = tk.BooleanVar()
        self.draw_fly.set(self.handler.options.draw_fly)
        self.draw_fly_checkbox = tk.Checkbutton(
            self,
            text="Fly",
            variable=self.draw_fly,
            command=self.toggle_draw_fly,
        )

        self.draw_distance = tk.BooleanVar()
        self.draw_distance.set(self.handler.options.draw_distance)
        self.draw_distance_checkbox = tk.Checkbutton(
            self,
            text="Distance",
            variable=self.draw_distance,
            command=self.toggle_draw_distance,
        )

        self.draw_well = tk.BooleanVar()
        self.draw_well.set(self.handler.options.draw_well)
        self.draw_well_checkbox = tk.Checkbutton(
            self,
            text="Well",
            variable=self.draw_well,
            command=self.toggle_draw_well,
        )

        self.row = None

    def layout(self, row):
        self.row = row
        self.grid(row=row, column=0)
        self.draw_index_checkbox.grid(row=0, column=0)
        self.draw_fly_checkbox.grid(row=0, column=1)
        self.draw_distance_checkbox.grid(row=0, column=2)
        self.draw_well_checkbox.grid(row=0, column=3)

    def toggle_draw_index(self):
        self.handler.options.toggle("draw_index")
        self.draw_index.set(self.handler.options.draw_index)

    def toggle_draw_fly(self):
        self.handler.options.toggle("draw_fly")
        self.draw_fly.set(self.handler.options.draw_fly)

    def toggle_draw_distance(self):
        self.handler.options.toggle("draw_distance")
        self.draw_distance.set(self.handler.options.draw_distance)

    def toggle_draw_well(self):
        self.handler.options.toggle("draw_well")
        self.draw_well.set(self.handler.options.draw_well)

    # triggered via hide button in RecordCanvas
    def toggle_hidden(self):
        self.handler.options.toggle("hidden")
        if self.handler.options.hidden:
            self.grid_forget()
        else:
            self.layout(self.row)
