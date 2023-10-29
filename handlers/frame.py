from typing import TYPE_CHECKING, Dict

import cv2

from custom_types.motion import MotionEvent, MotionEventHandler, MotionPoint
from detection.motion import MotionDetector

if TYPE_CHECKING:
    from components.root_window import RootWindow

# this class handles motion detected in frames and emits motion events
# at the moment, this class only handles a single motion event per grid item per frame,
# so we can only handle one fly per well, but this can be changed in the future
# see the logic in handle_contour for more info


class FrameHandler(MotionEvent):
    def __init__(self, window: "RootWindow", handler: MotionEventHandler):
        self.window = window
        try:
            self.grid = self.window.app_state["grid"]
        except KeyError:
            raise Exception("Grid not initialized")
        self.handler = handler
        self.motion_detector = MotionDetector(window.settings)

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

        point = MotionPoint(contour, item, frame_count)
        coords = point.item.coords
        last_point = self.points.get(coords)
        if last_point is None:
            self.points[coords] = point
            return

        # if we have multiple points in the same frame, we only want to keep the largest one
        # we'll need to change this if we ever want to capture multiple flies in a single well
        if point.frame_count == last_point.frame_count and point.area < last_point.area:
            return

        # emit event
        event = MotionEvent(
            point=point,
            last_point=last_point,
            item=item,
            frame=frame,
        )
        self.handler.handle(event)

        self.points[coords] = point

    def handle(self, frame, frame_count: int):
        if self.handler.on_frame:
            self.handler.on_frame(frame)
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
