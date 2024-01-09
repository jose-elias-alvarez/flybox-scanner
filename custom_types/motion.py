import cv2

from detection.grids import Item
from utils.geometry import calculate_distance_between, get_contour_center


class MotionPoint:
    def __init__(self, contour, item: Item, frame_count: int):
        self.contour = contour
        self.item = item
        self.frame_count = frame_count
        self.center = get_contour_center(contour)
        self.area = cv2.contourArea(contour)

    def distance_to(self, other: "MotionPoint"):
        return calculate_distance_between(self.center, other.center)


class MotionEvent:
    def __init__(
        self,
        point: MotionPoint,
        last_point: MotionPoint,
        item: Item,
        frame,
    ):
        self.point = point
        self.last_point = last_point
        self.item = item
        self.frame = frame
        self.raw_frame = frame.copy()
        self.distance = point.distance_to(last_point)


class MotionEventHandler:
    def __init__(self) -> None:
        self.on_frame = None

    def handle(self, event: MotionEvent) -> None:
        pass
