from handlers.frame import MotionEvent
from utils import draw_contour, draw_rectangle


def debug_handler(e: MotionEvent):
    draw_rectangle((e.point.item.start_point, e.point.item.end_point), e.frame)
    draw_contour(e.point.contour, e.frame)
