import datetime
from collections import defaultdict
from threading import Timer
from typing import TYPE_CHECKING

from custom_types.motion import MotionEvent, MotionEventHandler

OUT_DIR = "output"
DELIMITER = "\t"
DATE_FORMAT = "%d %b %y"
TIME_FORMAT = "%H:%M:%S"
DEFAULT_INTERVAL = 5

if TYPE_CHECKING:
    from components.root_window import RootWindow


def make_distances():
    return defaultdict(lambda: 0)


# captures motion events and flushes them to the specified file at the specified interval
class FileIntervalHandler(MotionEventHandler):
    def __init__(self, window: "RootWindow", filename: str, interval=DEFAULT_INTERVAL):
        self.window = window
        self.window.cleanup.put(self.cancel)

        self.filename = filename
        self.interval = interval
        self.index = 0
        self.distances = make_distances()

        # immediately write file (helps catch errors)
        with open(self.filename, "w") as f:
            f.write("")

    def start(self):
        self.timer = Timer(self.interval, self.flush)
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def handle(self, event: MotionEvent):
        self.distances[event.item.coords] += event.distance

    def make_row(self):
        timestamp = datetime.datetime.now()
        parts = [
            self.index,
            timestamp.strftime(DATE_FORMAT),
            timestamp.strftime(TIME_FORMAT),
            1,  # monitor status (always 1)
            0,  # unused
            1,  # monitor number (should be user-specified)
            0,  # unused
            "Ct",  # ??
            0,  # unused
            0,  # likely unused
        ]
        # add one column for each item in the grid
        for _, col in self.distances:
            parts.append(int(col))
        return DELIMITER.join(map(str, parts))

    def write_row(self, row: str):
        with open(self.filename, "a") as f:
            f.write(row + "\n")

    def flush(self):
        self.index += 1
        try:
            row = self.make_row()
            self.write_row(row)
            self.start()
        except Exception as e:
            self.window.errors.put(e)

        self.distances = make_distances()
