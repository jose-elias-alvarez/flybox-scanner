import cv2

from detection.motion import MotionDetector


class Point:
    def __init__(self, center, contour, item, coords, frame_count):
        self.center = center
        self.contour = contour
        self.item = item
        self.coords = coords
        self.frame_count = frame_count


class MotionEvent:
    def __init__(self, coords, distance, point, frame):
        self.coords = coords
        self.distance = distance
        self.point = point
        self.frame = frame

    def __repr__(self):
        return f"MotionEvent(coords={self.coords}, distance={self.distance})"


class FrameHandler:
    def __init__(self, grids, dimensions, handler):
        self.grids = grids
        self.dimensions = dimensions
        self.handler = handler

        self.points = [
            [[None for _ in range(dimensions[2])] for _ in range(dimensions[1])]
        ]
        self.motion_detector = MotionDetector()

    def find_item(self, center):
        (x, y) = center
        for grid_index, grid in enumerate(self.grids):
            for row_index, row in enumerate(grid):
                for item_index, item in enumerate(row):
                    if item[0][0] <= x <= item[1][0] and item[0][1] <= y <= item[1][1]:
                        return (item, (grid_index, row_index, item_index))

    def handle_contour(self, contour, frame, frame_count):
        center = self.motion_detector.get_center(contour)
        if center is None:
            return
        found = self.find_item(center)
        if found is None:
            return

        item = found[0]
        coords = found[1]

        point = Point(center, contour, item, coords, frame_count)
        last_point = self.points[coords[0]][coords[1]][coords[2]]

        if last_point is None:
            self.points[coords[0]][coords[1]][coords[2]] = point
            return

        # if we have 2 points in the same frame, only keep the larger one
        if point.frame_count == last_point.frame_count:
            if cv2.contourArea(point.contour) < cv2.contourArea(last_point.contour):
                return

        distance = cv2.norm(point.center, last_point.center)
        event = MotionEvent(coords, distance, point, frame)
        self.handler(event)

        # set last point
        self.points[coords[0]][coords[1]][coords[2]] = point

    def handle(self, frame, frame_count):
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
