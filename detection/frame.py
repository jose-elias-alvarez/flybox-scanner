import cv2

from custom_types import Frame

# we need to test performance on lab hardware
MAX_WIDTH = 640
MAX_HEIGHT = 480

# 0 is absolute black, 255 is absolute white
THRESH = 40


class FrameCropper:
    def __init__(self):
        self.boundary = None

    def crop_boundary(self, frame: Frame):
        if self.boundary is not None:
            x, y, w, h = self.boundary
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, threshold = cv2.threshold(gray, THRESH, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(
                threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
            self.boundary = (x, y, w, h)
        frame = frame[y : y + h, x : x + w]
        return frame

    def resize(self, frame: Frame):
        original_height, original_width = frame.shape[:2]
        aspect_ratio = original_width / original_height

        if (MAX_WIDTH / aspect_ratio) > MAX_HEIGHT:
            new_width = int(MAX_HEIGHT * aspect_ratio)
            new_height = MAX_HEIGHT
        else:
            new_height = int(MAX_WIDTH / aspect_ratio)
            new_width = MAX_WIDTH

        frame = cv2.resize(frame, (new_width, new_height))
        return frame


cropper = FrameCropper()


def crop(frame):
    frame = cropper.crop_boundary(frame)
    frame = cropper.resize(frame)
    return frame
