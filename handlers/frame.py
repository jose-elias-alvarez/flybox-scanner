from typing import TYPE_CHECKING, Dict

import cv2

from custom_types.motion import MotionEvent, MotionEventHandler, MotionPoint
from detection.motion import MotionDetector

if TYPE_CHECKING:
    from components.root_window import RootWindow


class FrameHandler(MotionEvent):
    def __init__(self, window: "RootWindow", handler: MotionEventHandler):
        self.window = window
        try:
            self.grid = self.window.app_state["grid"]
        except KeyError:
            raise Exception("Grid not initialized")
        self.handler = handler
        self.motion_detector = MotionDetector()

        self.points: Dict[tuple, MotionPoint] = {}
        self.average = 0

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
        last_point = self.points.get(coords)
        if last_point is None:
            self.points[coords] = point
            return

        # if we have 2 points in the same frame, only keep the larger one
        if point.frame_count == last_point.frame_count:
            if cv2.contourArea(point.contour) < cv2.contourArea(last_point.contour):
                return

        # calculate distance between two contours
        distance = cv2.matchShapes(
            point.contour, last_point.contour, cv2.CONTOURS_MATCH_I1, 0
        )
        # emit event
        event = MotionEvent(distance, point, item, frame)
        self.handler.handle(event)

        self.points[coords] = point

    def handle(self, frame, frame_count: int):
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
