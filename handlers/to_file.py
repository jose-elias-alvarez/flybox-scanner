import datetime
from typing import List

from detection.grids import Grid
from handlers.frame import MotionEvent
from handlers.resolution import MotionHandler

FILE_PATH = "data.txt"
DELIMITER = "\t"
DATE_FORMAT = "%d %b %y"
TIME_FORMAT = "%H:%M:%S"


class ToFileHandler(MotionHandler):
    def __init__(self, grid: Grid):
        self.grid = grid
        self.index = 0
        self.distances = self.make_empty_distances()

    def make_empty_distances(self) -> List[List[int]]:
        (rows, cols) = self.grid.dimensions
        distances = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                row.append(0)
            distances.append(row)
        return distances

    def on_event(self, event: MotionEvent):
        (row, col) = event.item.coords
        self.distances[row][col] += event.distance

    def make_row(self, time: datetime.datetime):
        parts = [
            self.index,
            time.strftime(DATE_FORMAT),
            time.strftime(TIME_FORMAT),
            1,  # monitor status (always 1)
            0,  # unused
            1,  # monitor number (should be user-specified)
            0,  # unused
            "Ct",  # ??
            0,  # unused
            0,  # likely unused
        ]
        # add one column for each item in the grid
        for row in self.distances:
            for col in row:
                parts.append(int(col))
        return DELIMITER.join(map(str, parts))

    def write_row(self, row: str):
        with open(FILE_PATH, "a") as f:
            f.write(row + "\n")

    def on_flush(self, timestamp: float):
        self.index += 1

        time = datetime.datetime.fromtimestamp(timestamp)
        row = self.make_row(time)
        self.write_row(row)

        self.distances = self.make_empty_distances()
