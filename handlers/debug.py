from utils import draw_circle, draw_contour, draw_rectangle


def debug_handler(e, actual=None):
    print(e)

    draw_rectangle(e.point.item, e.frame)
    draw_contour(e.point.contour, e.frame)

    circle = (e.point.center[0], e.point.center[1], 1)
    draw_circle(circle, e.frame)

    if actual is not None:
        actual(e)
