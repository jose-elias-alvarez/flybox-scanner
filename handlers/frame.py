from typing import Dict

import cv2

from custom_types.grid import Grid
from custom_types.motion import MotionEvent, MotionEventHandler, MotionPoint
from detection.motion import MotionDetector
from utils.app_settings import AppSettings

# this class handles motion detected in frames and emits motion events
# at the moment, this class only handles a single motion event per grid item per frame,
# so we can only handle one fly per well, but this can be changed in the future
# see the logic in handle_contour for more info


class FrameHandler(MotionEvent):
    def __init__(self, grid: Grid, settings: AppSettings, handler: MotionEventHandler):
        self.grid = grid
        self.motion_detector = MotionDetector(settings)
        self.handler = handler

        self.points: Dict[tuple, MotionPoint] = {}
        self.average = 0

    def find_item(self, contour):
        bounds = cv2.boundingRect(contour)
        row = self.grid.find_row(bounds)
        if row is None:
            return
        return row.find_item(bounds)

    def handle_contour(self, contour, frame, raw_frame, frame_count: int):
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
            raw_frame=raw_frame,
        )
        self.handler.handle(event)

        self.points[coords] = point

    def handle(self, frame, frame_count: int):
        contours = self.motion_detector.detect(frame)
        # this is a copy of the original frame used for image recording
        # don't modify it!
        raw_frame = frame.copy()
        for contour in contours:
            self.handle_contour(contour, frame, raw_frame, frame_count)
        # HACK: move this after contour detection so that changes to the frame don't affect detection
        # the fact that the same frame is used for detection *and* display is itself bad,
        # but this works for now
        if self.handler.on_frame:
            self.handler.on_frame(frame)
