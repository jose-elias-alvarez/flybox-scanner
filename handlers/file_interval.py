import datetime
from threading import Timer
from typing import TYPE_CHECKING

from custom_types.motion import MotionEvent, MotionEventHandler

if TYPE_CHECKING:
    from components.root_window import RootWindow

# this class handles motion events and flushes them to the specified file at the specified interval

# 60 is the canonical interval, but you may want to lower this for testing
DEFAULT_INTERVAL = 60

# output file options
# see the make_row method for more info
DATE_FORMAT = "%d-%b-%y"
TIME_FORMAT = "%I:%M:%S"
DELIMITER = "\t"


# captures motion events and flushes them to the specified file at the specified interval
class FileIntervalHandler(MotionEventHandler):
    def __init__(self, window: "RootWindow", filename: str, interval=DEFAULT_INTERVAL):
        self.window = window
        self.timer = None
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
        if self.timer is not None:
            self.timer.cancel()

    def handle(self, event: MotionEvent):
        self.distances[event.item.coords] += event.distance

    def make_distances(self):
        distances = {}
        for row in self.grid.rows:
            for item in row.items:
                distances[item.coords] = 0
        return distances

    def format_time(self, dt):
        time_str = dt.strftime("%I:%M:%S")
        if time_str[0] == "0":
            return time_str[1:]
        return time_str

    def make_row(self):
        row_parts = [
            self.index,
            self.last_flush.strftime(DATE_FORMAT),
            self.format_time(self.last_flush),
            1,  # monitor status (always 1)
            1,  # monitor number (should be user-specified in the future)
            0,  # unused
            0,  # unused
            0,  # unused
            0,  # unused
            "Ct",  # ??
            0,  # unused
        ]
        max_x = max(key[0] for key in self.distances)
        max_y = max(key[1] for key in self.distances)

        for y in range(max_y + 1):
            for x in range(max_x + 1):
                coords = (x, y)
                if coords in self.distances:
                    row_parts.append(int(self.distances[coords]))
                else:
                    row_parts.append(
                        0
                    )  # Default value if coords don't exist in the dictionary

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
