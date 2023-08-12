import datetime

FILE_PATH = "data.txt"
DELIMITER = "\t"


class ToFileHandler:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.grids = self.init_grids()
        self.index = 0

    def init_grids(self):
        (grid, rows, cols) = self.dimensions
        # initialize as a 3d array of 0s
        return [[[0 for _ in range(cols)] for _ in range(rows)] for _ in range(grid)]

    def on_event(self, e):
        (grid, x, y) = e.coords
        self.grids[grid][x][y] += e.distance

    def make_row(self, time):
        parts = [
            self.index,
            time.strftime("%d %b %y"),
            time.strftime("%H:%M:%S"),
            1,  # monitor status (always 1)
            0,  # unused
            1,  # monitor number (should be user-specified)
            0,  # unused
            "Ct",  # ??
            0,  # unused
            0,  # likely unused
        ]
        for grid in self.grids:
            for row in grid:
                for col in row:
                    parts.append(int(col))
        return DELIMITER.join(map(str, parts))

    def write_row(self, row):
        with open(FILE_PATH, "a") as f:
            f.write(row + "\n")

    def on_flush(self, timestamp):
        self.index += 1

        time = datetime.datetime.fromtimestamp(timestamp)
        row = self.make_row(time)
        self.write_row(row)

        self.grids = self.init_grids()
