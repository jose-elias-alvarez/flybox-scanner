import cv2
import numpy as np

from utils import draw_circle, draw_rectangle, show_frame

MAX_ITERATIONS = 100
MAX_CIRCLES = 96 * 2
MIN_CIRCLES = 12

CONVERGENCE_THRESHOLD = 0.0005

# put in a bunch of nonstandard colors here please, like 9 or 10
DEBUG_COLORS = (
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
    (0, 0, 128),
    (0, 128, 0),
    (128, 0, 0),
    (0, 128, 128),
    (128, 0, 128),
    (128, 128, 0),
)


class GridDetector:
    def __init__(self, frame):
        self.frame = frame
        self.processed_frame = self.process_frame()

    def process_frame(self):
        clahe = cv2.createCLAHE(clipLimit=4, tileGridSize=(8, 8))
        processed_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        processed_frame = clahe.apply(processed_frame)
        # it's recommended to use blurring here,
        # but it seems to make the first detection phase less consistent
        # processed_frame = cv2.GaussianBlur(processed_frame, (5, 5), 0)
        return processed_frame

    def get_approximate_average_radius(self):
        # use conservative values
        param1 = 40
        param2 = 50
        # we start by assuming that the frame contains at most MAX_CIRCLES
        # and at least MIN_CIRCLES
        max_radius = int(min(self.frame.shape[0], self.frame.shape[1]) / MIN_CIRCLES)
        min_radius = int(min(self.frame.shape[0], self.frame.shape[1]) / MAX_CIRCLES)
        min_dist = min_radius * 2
        # on each iteration, we update the parameters
        # using the average radius of the circles we detected
        iterations = 0
        # we also keep track of the last average radius so we can exit early
        # once we've converged
        last_average_radius = float("inf")
        while iterations < MAX_ITERATIONS:
            iterations += 1
            detected = cv2.HoughCircles(
                self.processed_frame,
                cv2.HOUGH_GRADIENT,
                1,
                min_dist,
                param1=param1,
                param2=param2,
                minRadius=min_radius,
                maxRadius=max_radius,
            )
            if detected is None:
                continue
            average_radius = np.average(detected[0, :, 2])
            # if our new average is (almost) the same as the old average, we're done
            if abs(average_radius - last_average_radius) < CONVERGENCE_THRESHOLD:
                break
            # if our new average is much larger than the old average,
            # we most likely have a bad detection,
            # so we ignore it and try again
            if average_radius > last_average_radius * 1.05:
                continue

            # update values
            min_radius = int(average_radius * 0.5)
            max_radius = int(average_radius * 1.5)
            min_dist = min_radius * 2
            last_average_radius = average_radius

            # draw circles at each step so users don't think the program has frozen
            # (and because it looks cool)
            copy = self.frame.copy()
            for circle in detected[0]:
                draw_circle(circle, copy, (255, 0, 0))
            show_frame(copy, 75)

        if last_average_radius == float("inf"):
            raise Exception("No circles detected")
        return last_average_radius

    def detect_circles(self):
        approximate_average_radius = self.get_approximate_average_radius()
        # now that we have an approximate radius, we can keep our radius tighter
        min_radius = int(approximate_average_radius * 0.85)
        max_radius = int(approximate_average_radius * 1.15)
        min_dist = min_radius * 2
        detected = cv2.HoughCircles(
            self.processed_frame,
            cv2.HOUGH_GRADIENT,
            1,
            min_dist,
            param1=10,
            param2=20,  # now we can make this looser
            minRadius=min_radius,
            maxRadius=max_radius,
        )
        if detected is None:
            raise Exception("No circles detected")
        circles = detected[0]

        copy = self.frame.copy()
        for circle in circles:
            draw_circle(circle, copy, (0, 255, 0))
        show_frame(copy, 500)
        return circles

    def detect(self):
        circles = self.detect_circles()
        average_radius = np.average(circles[:, 2])
        # our first goal: convert each detected circle into a rectangular grid item,
        # and sort each item into a grid
        grids = [[]]
        # if a circle's x position is too far from the center of the previous circle,
        # we'll know we've reached a new circle,
        # so we start by sorting by x position
        for x, y, radius in sorted(circles, key=lambda circle: circle[0]):
            # lighting can cause variations beyond what we expect,
            # so we smooth out the radius using a weighted average
            radius = (radius * 0.25) + (average_radius * 0.75)
            item = (
                (
                    x - radius,
                    y - radius,
                ),
                (
                    x + radius,
                    y + radius,
                ),
            )
            # case 1: no items in grid, so we can't make a comparison
            last_grid = grids[-1]
            if len(last_grid) == 0:
                last_grid.append(item)
                continue
            # case 2: item is too far from last item on the x axis, so we're in a new grid
            last_item = last_grid[-1]
            distance = item[1][0] - last_item[1][0]
            # this is sort of arbitrary and could need tweaking depending on actual grid dimensions
            is_in_new_grid = distance > average_radius * 2.5
            if is_in_new_grid:
                grids.append([item])
                continue
            # case 3: item is close enough to last item, so we're still in the same grid
            last_grid.append(item)

        # our next goal is to organize each grid into rows
        for i, grid in enumerate(grids):
            # this time we'll use the y position to determine if we're in a new row
            grid.sort(key=lambda item: item[0][1])
            organized_grid = [[]]
            for item in grid:
                row = organized_grid[-1]
                # case 1: no items in row yet, so we can't make a comparison
                if len(row) == 0:
                    row.append(item)
                    continue
                # case 2: item is too far from last item on the y axis, so we're in a new row
                last_item = row[-1]
                distance = item[1][1] - last_item[1][1]
                is_in_new_row = distance > average_radius
                if is_in_new_row:
                    organized_grid.append([item])
                    continue
                # case 3: item is close enough to last item, so we're still in the same row
                row.append(item)
            grids[i] = organized_grid

        # finally, we peform some basic validation and sort each row by x position
        for grid_index, grid in enumerate(grids):
            grid_start = (float("inf"), float("inf"))
            grid_end = (0, 0)
            # validate that each grid contains the same number of rows
            if len(grid) != len(grids[0]):
                raise Exception(
                    f"Invalid number of rows (expected {len(grids[0])}, got {len(grid)})"
                )
            for row_index, row in enumerate(grid):
                # validate that each row contains the same number of items
                if len(row) != len(grid[0]):
                    raise Exception(
                        f"Invalid number of items in row (expected {len(grid[0])}, got {len(row)})"
                    )
                for item_index, item in enumerate(row):
                    # compare to grid_start and grid_end and update as needed
                    grid_start = (
                        min(grid_start[0], item[0][0]),
                        min(grid_start[1], item[0][1]),
                    )
                    grid_end = (
                        max(grid_end[0], item[1][0]),
                        max(grid_end[1], item[1][1]),
                    )
                    # draw each item, color doesn't matter
                    draw_rectangle(item, self.frame, (0, 255, 0), 2)

                row.sort(key=lambda item: item[0])
                # draw each row in a different color
                color = DEBUG_COLORS[row_index % len(DEBUG_COLORS)]
                draw_rectangle((row[0][0], row[-1][1]), self.frame, color)

            # draw each grid in a different color
            color = DEBUG_COLORS[grid_index % len(DEBUG_COLORS)]
            draw_rectangle((grid_start, grid_end), self.frame, color)

        show_frame(self.frame, 500)

        dimensions = (
            len(grids),
            len(grids[0]),
            len(grids[0][0]),
        )
        return grids, dimensions
