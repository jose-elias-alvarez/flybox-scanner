from typing import List, Tuple

from custom_types.contour import ContourBounds
from custom_types.geometry import Rectangle


class GridComponent:
    def contains(self, contour_bounds: ContourBounds):
        raise NotImplementedError()

    @property
    def bounds(self) -> Rectangle:
        raise NotImplementedError()

    def contains(self, contour_bounds: ContourBounds):
        (x, y, w, h) = contour_bounds
        (start_point, end_point) = self.bounds
        return (
            start_point[0] <= x <= end_point[0]
            and start_point[1] <= y <= end_point[1]
            and x + w <= start_point[0] + end_point[0]
            and y + h <= start_point[1] + end_point[1]
        )


class Item(GridComponent):
    def __init__(self, rectangle: Rectangle, coords: Tuple[int, int]):
        self.start_point = rectangle[0]
        self.end_point = rectangle[1]
        self.coords = coords

    @property
    def bounds(self) -> Rectangle:
        return (self.start_point, self.end_point)


class Row(GridComponent):
    def __init__(self, items: List[Item]):
        self.items = items

    def __len__(self):
        return len(self.items)

    @property
    def bounds(self) -> Rectangle:
        return (
            (
                self.items[0].start_point[0],
                self.items[0].start_point[1],
            ),
            (
                self.items[-1].end_point[0],
                self.items[-1].end_point[1],
            ),
        )

    def find_item(self, bounds: ContourBounds):
        for item in self.items:
            if item.contains(bounds):
                return item
        return None


class Grid(GridComponent):
    def __init__(self, rows: List[Row]):
        self.rows = rows

    @property
    def bounds(self) -> Rectangle:
        return (
            (
                self.rows[0].items[0].start_point[0],
                self.rows[0].items[0].start_point[1],
            ),
            (
                self.rows[-1].items[-1].end_point[0],
                self.rows[-1].items[-1].end_point[1],
            ),
        )

    def find_row(self, contour_bounds: ContourBounds):
        for row in self.rows:
            if row.contains(contour_bounds):
                return row
        return None

    @property
    def dimensions(self):
        return (len(self.rows), len(self.rows[0].items))
