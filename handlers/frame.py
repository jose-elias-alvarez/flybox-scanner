import cv2

from detection.motion import MotionDetector


class Point:
    def __init__(self, contour, item, coords, frame_count):
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
            for _ in range(dimensions[0])
        ]
        self.motion_detector = MotionDetector()
        self.average = 0

    def find_item(self, contour):
        x, y, w, h = cv2.boundingRect(contour)
        for grid_index, grid in enumerate(self.grids):
            for row_index, row in enumerate(grid):
                for item_index, item in enumerate(row):
                    (x1_rect, y1_rect), (x2_rect, y2_rect) = item
                    if (
                        x >= x1_rect
                        and y >= y1_rect
                        and (x + w) <= x2_rect
                        and (y + h) <= y2_rect
                    ):
                        return (item, (grid_index, row_index, item_index))

    def handle_contour(self, contour, frame, frame_count):
        found = self.find_item(contour)
        if found is None:
            return
        # calculate size
        size = cv2.contourArea(contour)
        # compare size to average
        # if it's smaller than 0.8 * average or larger than 1.2 * average, ignore it
        if self.average > 0:
            if size < 0.33 * self.average or size > 3 * self.average:
                return

        # update average
        self.average = (self.average + size) / 2

        item = found[0]
        coords = found[1]

        point = Point(contour, item, coords, frame_count)
        last_point = self.points[coords[0]][coords[1]][coords[2]]

        if last_point is None:
            self.points[coords[0]][coords[1]][coords[2]] = point
            return

        # if we have 2 points in the same frame, only keep the larger one
        if point.frame_count == last_point.frame_count:
            if cv2.contourArea(point.contour) < cv2.contourArea(last_point.contour):
                return

        # calculate distance between two contours
        distance = cv2.matchShapes(
            point.contour, last_point.contour, cv2.CONTOURS_MATCH_I1, 0
        )
        event = MotionEvent(coords, distance, point, frame)
        self.handler(event)

        # set last point
        self.points[coords[0]][coords[1]][coords[2]] = point

    def handle(self, frame, frame_count):
        contours = self.motion_detector.detect(frame)
        for contour in contours:
            self.handle_contour(contour, frame, frame_count)
