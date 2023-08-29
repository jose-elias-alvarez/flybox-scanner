import datetime
from collections import defaultdict
from threading import Timer
from typing import TYPE_CHECKING

from custom_types.motion import MotionEvent, MotionEventHandler

if TYPE_CHECKING:
    from components.root_window import RootWindow

# this class handles motion events and flushes them to the specified file at the specified interval

# 30 is the canonical interval, but you may want to lower this for testing
DEFAULT_INTERVAL = 30

# output file options
# see the make_row method for more info
DELIMITER = "\t"
DATE_FORMAT = "%d %b %y"
TIME_FORMAT = "%H:%M:%S"


# captures motion events and flushes them to the specified file at the specified interval
class FileIntervalHandler(MotionEventHandler):
    def __init__(self, window: "RootWindow", filename: str, interval=DEFAULT_INTERVAL):
        self.window = window
        self.window.cleanup.put(self.cancel)
        try:
            self.grid = self.window.app_state["grid"]
        except KeyError:
            raise Exception("Grid not initialized")
        self.filename = filename
        self.interval = interval
        self.index = 0
        self.distances = self.make_distances()
        self.last_flush = datetime.datetime.now()
        


        # immediately write file (provides better feedback, and helps catch errors)
        with open(self.filename, "w") as f:
            f.write("")

    def start(self):
        self.timer = Timer(self.interval, self.flush)
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def handle(self, event: MotionEvent):
        self.distances[event.item.coords] += event.distance

    def make_distances(self):
        # Assuming self.grid.rows returns a list of rows and each row has a method or property called "items" 
        # that returns a list of grid items. Further assuming each grid item has a property called "coords" 
        # which is a tuple representing its coordinates.
        first_coord = self.grid.rows[0].items[0].coords
        last_row = self.grid.rows[-1]
        last_coord = last_row.items[-1].coords

        distances = {}
        for i in range(first_coord[0], last_coord[0] + 1):
            for j in range(first_coord[1], last_coord[1] + 1):
                distances[(i, j)] = 0

        return distances

    def make_row(self):
        row_parts = [
            self.index,
            self.last_flush.strftime(DATE_FORMAT),
            self.last_flush.strftime(TIME_FORMAT),
            1,  # monitor status (always 1)
            0,  # unused
            1,  # monitor number (should be user-specified in the future)
            0,  # unused
            "Ct",  # ??
            0,  # unused
            0,  # likely unused
        ]
        # add one column for each item in the grid
        for key, distance in sorted(self.distances.items()):
            row_parts.append(int(distance))
        return DELIMITER.join(map(str, row_parts))

    def write_data(self):
        row = self.make_row()
        with open(self.filename, "a") as f:
            f.write(row + "\n")

    def flush(self):
        self.index += 1
        self.last_flush = datetime.datetime.now()
        try:
            self.write_data()
            self.start()
        except Exception as e:
            # since we're running in a thread, we add them to the queue to be handled on the next loop
            self.window.errors.put(e)

        self.distances = self.make_distances()
