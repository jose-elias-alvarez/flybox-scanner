from tkinter import Grid
from typing import Callable

import cv2
import numpy as np

from custom_types.motion import MotionEventHandler
from handlers.frame import MotionEvent

# this class wraps a motion event handler to add debug info
# at the moment, we're using it to show the detected fly and well
# this doesn't really cause as much slowdown as you'd imagine
# and if performance is important, we can hide the video altogether

SHOULD_DRAW_WELL = False
WELL_COLOR = (0, 255, 0)  # CV2 uses BGR because it hates you
WELL_THICKNESS = 1

SHOULD_DRAW_FLY = True
FLY_COLOR = (255, 0, 0)
FLY_THICKNESS = 2
LAST_FLY_COLOR = (128, 128, 128)
LAST_FLY_THICKNESS = 1

SHOULD_DRAW_DISTANCE = True
DISTANCE_COLOR = (0, 0, 255)
DISTANCE_THICKNESS = 1

SHOULD_DRAW_INDICES = True
INDEX_THICKNESS = 0.5
INDEX_COLOR = (255, 255, 255)

SHOULD_PRINT = False  # this is really noisy, so it's disabled by default


class DebugHandler(MotionEventHandler):
    def __init__(
        self, grid: Grid, handler: MotionEventHandler, is_visible: Callable[[], bool]
    ):
        self.grid = grid
        self.handler = handler
        self.is_visible = is_visible

        if SHOULD_DRAW_INDICES:
            self.overlay = None
            self.on_frame = self.draw_indices

    def draw_indices(self, frame):
        if not self.is_visible():
            return

        if self.overlay is None:
            self.overlay = np.zeros(frame.shape, dtype=np.uint8)
            for row in self.grid.rows:
                for item in row.items:
                    cv2.putText(
                        self.overlay,
                        str(item.index + 1),
                        (int(item.bounds[0][0]), int(item.bounds[0][1])),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        INDEX_THICKNESS,
                        INDEX_COLOR,
                    )

        cv2.bitwise_or(frame, self.overlay, frame)

    def draw_well(self, event: MotionEvent):
        (start, end) = event.point.item.bounds
        (x1, y1) = start
        (x2, y2) = end
        cv2.rectangle(
            event.frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            WELL_COLOR,
            WELL_THICKNESS,
        )

    def draw_fly(self, event: MotionEvent):
        cv2.drawContours(
            event.frame, [event.point.contour], -1, FLY_COLOR, FLY_THICKNESS
        )
        cv2.drawContours(
            event.frame,
            [event.last_point.contour],
            -1,
            LAST_FLY_COLOR,
            LAST_FLY_THICKNESS,
        )

    def draw_distance(self, event: MotionEvent):
        cv2.line(
            event.frame,
            (int(event.point.center[0]), int(event.point.center[1])),
            (int(event.last_point.center[0]), int(event.last_point.center[1])),
            DISTANCE_COLOR,
            DISTANCE_THICKNESS,
        )

    def handle(self, event: MotionEvent):
        self.handler.handle(event)
        if not self.is_visible():
            return

        if SHOULD_DRAW_WELL:
            self.draw_well(event)
        if SHOULD_DRAW_FLY:
            self.draw_fly(event)
        if SHOULD_DRAW_DISTANCE:
            self.draw_distance(event)
        if SHOULD_PRINT:
            print(event)
