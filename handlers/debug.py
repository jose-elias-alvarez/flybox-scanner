import cv2

from custom_types.motion import MotionEventHandler
from handlers.frame import MotionEvent

# this class wraps a motion event handler to add debug info
# at the moment, we're using it to show the detected fly and well
# this doesn't really cause as much slowdown as you'd imagine
# and if performance is important, we can hide the video altogether

SHOULD_DRAW_WELL = True
WELL_COLOR = (0, 255, 0)  # CV2 uses BGR because it hates you
WELL_THICKNESS = 1

SHOULD_DRAW_FLY = True
FLY_COLOR = (255, 0, 0)
FLY_THICKNESS = 2

SHOULD_DRAW_DISTANCE = True
DISTANCE_COLOR = (0, 0, 255)
DISTANCE_THICKNESS = 1
# only show distances above this threshold
DISTANCE_THRESHOLD = 0.05

SHOULD_PRINT = False  # this is really noisy, so it's disabled by default


class DebugHandler(MotionEventHandler):
    def __init__(self, handler: MotionEventHandler):
        self.handler = handler

    def draw_well(self, event: MotionEvent):
        (start, end) = (event.point.item.start_point, event.point.item.end_point)
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

    def draw_distance(self, event: MotionEvent):
        if event.distance < DISTANCE_THRESHOLD:
            return
        start_point = event.point.item.bounds[0]
        start_point = (int(start_point[0]), int(start_point[1]))
        cv2.putText(
            event.frame,
            f"{event.distance:.2f}",
            start_point,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            DISTANCE_COLOR,
            DISTANCE_THICKNESS,
        )

    def handle(self, event: MotionEvent):
        self.handler.handle(event)
        if SHOULD_DRAW_WELL:
            self.draw_well(event)
        if SHOULD_DRAW_FLY:
            self.draw_fly(event)
        if SHOULD_DRAW_DISTANCE:
            self.draw_distance(event)
        if SHOULD_PRINT:
            print(event)
