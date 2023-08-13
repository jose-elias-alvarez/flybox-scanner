import cv2

from handlers.frame import MotionEvent


def draw_rectangle(rect, frame):
    (start, end) = rect
    (x1, y1) = start
    (x2, y2) = end
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)


def draw_contour(contour, frame):
    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)


def debug_handler(e: MotionEvent):
    draw_rectangle((e.point.item.start_point, e.point.item.end_point), e.frame)
    draw_contour(e.point.contour, e.frame)
