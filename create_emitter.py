import cv2

# not sure this is really necessary
MIN_DISTANCE = 0.00


class MotionEvent:
    def __init__(self, box, row, well, contour, distance, frame_count):
        self.box = box
        self.row = row
        self.well = well
        self.distance = distance
        self.contour = contour
        self.frame_count = frame_count

    def __repr__(self):
        return f"MotionEvent(box={self.box}, row={self.row}, well={self.well}, distance={self.distance}, frame_count={self.frame_count})"


def create_matrix(wells):
    matrix = []
    for box in wells:
        matrix.append([])
        for row in box:
            matrix[-1].append([])
            for well in row:
                matrix[-1][-1].append(None)
    return matrix


def create_emitter(wells, callback):
    matrix = create_matrix(wells)

    def emitter(coords, contour, frame_count):
        box, row, col = coords
        last = matrix[box][row][col]
        if last is None:
            matrix[box][row][col] = (contour, frame_count)
            return
        last_contour, last_frame_count = last
        if frame_count == last_frame_count:
            # compare sizes and only keep larger
            if cv2.contourArea(contour) <= cv2.contourArea(last_contour):
                return
        # calculate distance between contours
        distance = cv2.matchShapes(contour, last_contour, cv2.CONTOURS_MATCH_I1, 0)
        e = MotionEvent(box, row, col, contour, distance, frame_count)
        callback(e)

        matrix[box][row][col] = (contour, frame_count)
        return e

    return emitter
