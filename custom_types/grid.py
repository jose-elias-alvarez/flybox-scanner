from typing import List, Tuple

from custom_types.contour import ContourBounds
from custom_types.geometry import Rectangle


class GridComponent:
    def contains(self, contour_bounds: ContourBounds):
        try:
            (start_point, end_point) = self.bounds
        except AttributeError:
            raise Exception(f"GridComponent {self} does not have bounds")
        (x, y, w, h) = contour_bounds
        return (
            start_point[0] <= x <= end_point[0]
            and start_point[1] <= y <= end_point[1]
            and x + w <= start_point[0] + end_point[0]
            and y + h <= start_point[1] + end_point[1]
        )


class Item(GridComponent):
    def __init__(self, rectangle: Rectangle, index: int, coords: Tuple[int, int]):
        self.index = index
        self.bounds = rectangle
        self.coords = coords


class Row(GridComponent):
    def __init__(self, items: List[Item]):
        self.items = items
        self.bounds = self.calculate_bounds()

    def __len__(self):
        return len(self.items)

    def calculate_bounds(self):
        if len(self.items) == 0:
            return ((0, 0), (0, 0))
        start_point = (float("inf"), float("inf"))
        end_point = (float("-inf"), float("-inf"))
        for item in self.items:
            (x, y) = item.bounds[0]
            if x < start_point[0]:
                start_point = (x, start_point[1])
            if y < start_point[1]:
                start_point = (start_point[0], y)
            (x, y) = item.bounds[1]
            if x > end_point[0]:
                end_point = (x, end_point[1])
            if y > end_point[1]:
                end_point = (end_point[0], y)
        return (start_point, end_point)

    def find_item(self, bounds: ContourBounds):
        for item in self.items:
            if item.contains(bounds):
                return item
        return None


class Grid(GridComponent):
    def __init__(self, rows: List[Row]):
        self.rows = rows
        self.bounds = self.calculate_bounds()

    def calculate_bounds(self):
        if len(self.rows) == 0:
            return ((0, 0), (0, 0))
        start_point = (float("inf"), float("inf"))
        end_point = (float("-inf"), float("-inf"))
        for row in self.rows:
            (x, y) = row.bounds[0]
            if x < start_point[0]:
                start_point = (x, start_point[1])
            if y < start_point[1]:
                start_point = (start_point[0], y)
            (x, y) = row.bounds[1]
            if x > end_point[0]:
                end_point = (x, end_point[1])
            if y > end_point[1]:
                end_point = (end_point[0], y)
        return (start_point, end_point)

    def find_row(self, contour_bounds: ContourBounds):
        for row in self.rows:
            if row.contains(contour_bounds):
                return row
        return None

    @property
    def dimensions(self):
        return (len(self.rows), len(self.rows[0].items))
