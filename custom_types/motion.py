from detection.grids import Item


class MotionPoint:
    def __init__(self, contour, item: Item, frame_count: int):
        self.contour = contour
        self.item = item
        self.frame_count = frame_count


class MotionEvent:
    def __init__(self, distance: int, point: MotionPoint, item: Item, frame):
        self.distance = distance
        self.point = point
        self.item = item
        self.frame = frame


class MotionEventHandler:
    def handle(event: "MotionEvent") -> None:
        raise NotImplementedError()
