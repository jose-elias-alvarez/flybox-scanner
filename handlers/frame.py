from typing import TYPE_CHECKING, Dict

import cv2

from custom_types.motion import MotionEvent, MotionEventHandler, MotionPoint
from detection.motion import MotionDetector
from utils.geometry import calculate_distance_between, get_contour_center

if TYPE_CHECKING:
    from components.root_window import RootWindow

# this class handles motion detected in frames and emits motion events
# at the moment, this class only handles a single motion event per grid item per frame,
# so we can only handle one fly per well, but this can be changed in the future
# see the logic in handle_contour for more info

# we can keep a running average of the size of detected contours
# to filter out detected contours that are too large or too small,
# since these are likely false positives
SHOULD_FILTER_BY_AVERAGE = True
FILTER_BY_AVERAGE_BOTTOM = 0.33
FILTER_BY_AVERAGE_TOP = 3


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
        if SHOULD_FILTER_BY_AVERAGE:
            if self.average > 0:
                if (
                    size < FILTER_BY_AVERAGE_BOTTOM * self.average
                    or size > FILTER_BY_AVERAGE_TOP * self.average
                ):
                    return
            self.average = (self.average + size) / 2

        point = MotionPoint(contour, item, frame_count)
        coords = point.item.coords
        last_point = self.points.get(coords)
        if last_point is None:
            self.points[coords] = point
            return

        # if we have multiple points in the same frame, we only want to keep the largest one
        # we'll need to change this if we ever want to capture multiple flies in a single well
        if point.frame_count == last_point.frame_count:
            if cv2.contourArea(point.contour) < cv2.contourArea(last_point.contour):
                return

        center = get_contour_center(contour)
        last_center = get_contour_center(last_point.contour)
        if not (center and last_center):
            return
        distance = calculate_distance_between(center, last_center)

        event = MotionEvent(distance, point, item, frame)
        self.handler.handle(event)

        self.points[coords] = point

    def handle(self, frame, frame_count: int):
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
