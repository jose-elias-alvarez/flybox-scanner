from utils import draw_circle, draw_contour, draw_rectangle


def debug_handler(e):
    # print(e)

    draw_rectangle(e.point.item, e.frame)
    draw_contour(e.point.contour, e.frame)
