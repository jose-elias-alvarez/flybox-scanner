import cv2
import numpy as np

from custom_types import Contour, Frame


class MotionDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=1000, dist2Threshold=200, detectShadows=False
        )
        self.kernel = np.ones((3, 3), np.uint8)

    def get_bg_mask(self, frame: Frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        mask = cv2.medianBlur(mask, 5)
        return mask

    def get_center(self, contour: Contour):
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return
        x = M["m10"] / M["m00"]
        y = M["m01"] / M["m00"]
        return (x, y)

    def detect(self, frame: Frame):
        bg_mask = self.get_bg_mask(frame)
        (contours, _) = cv2.findContours(
            bg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
