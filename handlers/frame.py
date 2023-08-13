from typing import Callable, List

import cv2

from detection.grids import Grid, Item
from detection.motion import MotionDetector


class MotionHandler:
    def on_event(self, event: "MotionEvent") -> None:
        raise NotImplementedError()

    def on_flush(self, timestamp: float) -> None:
        raise NotImplementedError()


EventHandler = Callable[["MotionEvent"], None]


class MotionPoint:
    def __init__(self, contour, item: Item, frame_count: int):
        self.contour = contour
        self.item = item
        self.frame_count = frame_count


class MotionEvent:
    def __init__(self, distance: int, point: MotionPoint, item: Item, frame):
        self.distance = distance
        self.point = point
        self.item = item
        self.frame = frame


class FrameHandler:
    def __init__(self, grid: Grid, handler: EventHandler):
        self.handler = handler
        self.grid = grid
        self.motion_detector = MotionDetector()

        self.points = self.init_points()
        self.average = 0

    def init_points(self) -> List[List[None | MotionPoint]]:
        (rows, cols) = self.grid.dimensions
        points = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                row.append(None)
            points.append(row)
        return points

    def find_item(self, contour):
        bounds = cv2.boundingRect(contour)
        row = self.grid.find_row(bounds)
        if row is None:
            return
        return row.find_item(bounds)

    def handle_contour(self, contour, frame, frame_count: int):
        item = self.find_item(contour)
        if item is None:
            return
        size = cv2.contourArea(contour)
        # compare size to average
        if self.average > 0:
            if size < 0.33 * self.average or size > 3 * self.average:
                return
        self.average = (self.average + size) / 2

        point = MotionPoint(contour, item, frame_count)
        coords = point.item.coords
        last_point = self.points[coords[0]][coords[1]]
        if last_point is None:
            self.points[coords[0]][coords[1]] = point
            return

        # if we have 2 points in the same frame, only keep the larger one
        if point.frame_count == last_point.frame_count:
            if cv2.contourArea(point.contour) < cv2.contourArea(last_point.contour):
                return

        # calculate distance between two contours
        distance = cv2.matchShapes(
            point.contour, last_point.contour, cv2.CONTOURS_MATCH_I1, 0
        )
        event = MotionEvent(distance, point, item, frame)
        self.handler(event)

        self.points[coords[0]][coords[1]] = point

    def handle(self, frame, frame_count: int):
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
