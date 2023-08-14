import cv2

from custom_types.motion import MotionEventHandler
from handlers.frame import MotionEvent


def draw_rectangle(rect, frame):
    (start, end) = rect
    (x1, y1) = start
    (x2, y2) = end
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)


def draw_contour(contour, frame):
    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)


# wrap MotionEventHandler to add debug info
class DebugHandler(MotionEventHandler):
    def __init__(self, handler: MotionEventHandler):
        self.handler = handler

    def handle(self, event: MotionEvent):
        self.handler.handle(event)

        # print(event)
        draw_rectangle(
            (event.point.item.start_point, event.point.item.end_point), event.frame
        )
        draw_contour(event.point.contour, event.frame)
