from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from components.root_window import RootWindow

# this class is responsible for detecting motion in a frame
# it supports two methods:
# 1. background subtraction (pretty good)
# 2. frame differencing (experimental, not recommended)


class MotionDetector:
    def __init__(self, window: "RootWindow"):
        self.window = window
        self.last_frame = None

        # keep these hardcoded for now
        self.method = "BG_SUBTRACTOR"
        self.operation = cv2.MORPH_CLOSE

        self.kernel_size = self.window.settings.get("motion.kernel_size")
        self.blur_size = self.window.settings.get("motion.blur_size")
        self.history = self.window.settings.get("motion.history")
        self.dist2_threshold = self.window.settings.get("motion.dist2_threshold")
        self.diff_threshold = self.window.settings.get("motion.diff_threshold")

        self.kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=self.history,
            dist2Threshold=self.dist2_threshold,
            detectShadows=False,
        )

    def get_bg_mask(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        mask = cv2.morphologyEx(mask, self.operation, self.kernel, iterations=1)
        if self.blur_size > 0:
            mask = cv2.medianBlur(mask, self.blur_size)
        return mask

    def find_contours(self, frame):
        (contours, _) = cv2.findContours(
            frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    def detect_with_bg_subtractor(self, frame):
        mask = self.get_bg_mask(frame)
        return self.find_contours(mask)

    def detect_with_diff(self, frame):
        # small caveat: we drop the first frame
        # if we use this and want to get really picky about timing, we'll want to wait before recording
        if self.last_frame is None:
            self.last_frame = frame.copy()
            return []

        grayA = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(grayB, grayA)
        _, thresh = cv2.threshold(diff, self.diff_threshold, 255, cv2.THRESH_BINARY)
        # we use dilation instead of closing, since we want to expand the area of motion for contour detection
        thresh = cv2.dilate(thresh, iterations=2)

        self.last_frame = frame.copy()
        return self.find_contours(thresh)

    def detect(self, frame):
        if self.method == "BG_SUBTRACTOR":
            return self.detect_with_bg_subtractor(frame)
        elif self.method == "DIFF":
            return self.detect_with_diff(frame)
        else:
            raise ValueError(f"Invalid method: {self.method}")

    # debug methods used to tune motion detection
    def update_kernel_size(self, size):
        self.kernel_size = int(size)
        self.kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)

    def update_iterations(self, iterations):
        self.iterations = int(iterations)

    def update_blur_size(self, size):
        size = int(size)
        # make sure positive values are odd
        if size > 0 and size % 2 == 0:
            size += 1
        self.blur_size = size

    def update_history(self, history):
        self.history = int(history)
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=self.history,
            dist2Threshold=self.dist2_threshold,
            detectShadows=False,
        )

    def update_dist2_threshold(self, dist2_threshold):
        self.dist2_threshold = int(dist2_threshold)
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=self.history,
            dist2Threshold=self.dist2_threshold,
            detectShadows=False,
        )

    def save_settings(self):
        self.window.settings.set("motion.kernel_size", self.kernel_size)
        self.window.settings.set("motion.blur_size", self.blur_size)
        self.window.settings.set("motion.history", self.history)
        self.window.settings.set("motion.dist2_threshold", self.dist2_threshold)
        self.window.settings.save()
