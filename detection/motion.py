import cv2
import numpy as np

# this class is responsible for detecting motion in a frame
# at the moment, it supports two methods:
# 1. background subtraction
# 2. frame differencing (experimental, not recommended)

METHOD = "BG_SUBTRACTOR"
OPERATION = cv2.MORPH_CLOSE
# see the README for details on tuning these parameters
HISTORY = 12000
DIST2_THRESHOLD = 165
KERNEL_SIZE = 12
SHOULD_BLUR = True
BLUR_SIZE = 5

# we can also use a simple frame differencing method,
# where we compare each frame to the previous frame
# this is theoretically the most sensitive method,
# but the resulting motion is much jerkier,
# so this requires more tuning before we can use it
# METHOD = "DIFF"
DIFF_THRESHOLD = 15


class MotionDetector:
    def __init__(self):
        self.kernel_size = KERNEL_SIZE
        self.kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        self.operation = OPERATION
        self.should_blur = SHOULD_BLUR
        self.blur_size = BLUR_SIZE

        self.history = HISTORY
        self.dist2_threshold = DIST2_THRESHOLD
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=self.history,
            dist2Threshold=self.dist2_threshold,
            detectShadows=False,
        )

        self.last_frame = None

    def get_bg_mask(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        if self.operation is not None:
            mask = cv2.morphologyEx(mask, self.operation, self.kernel, iterations=1)
        if self.should_blur:
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
        # if we get really picky about timing, we'll want to wait before recording
        if self.last_frame is None:
            self.last_frame = frame.copy()
            return []

        grayA = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(grayB, grayA)
        _, thresh = cv2.threshold(diff, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
        # this is a dilation operation,
        # which expands the detected motion to make it more visible for contour detection
        # at the cost of making it less precise
        thresh = cv2.dilate(thresh, iterations=2)

        self.last_frame = frame.copy()
        return self.find_contours(thresh)

    def detect(self, frame):
        if METHOD == "BG_SUBTRACTOR":
            return self.detect_with_bg_subtractor(frame)
        elif METHOD == "DIFF":
            return self.detect_with_diff(frame)
        else:
            raise Exception(f"Invalid method: {METHOD}")

    # debug methods used to tune motion detection
    def update_kernel_size(self, size):
        self.kernel_size = int(size)
        self.kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)

    def update_iterations(self, iterations):
        self.iterations = int(iterations)

    def update_blur_size(self, size):
        size = int(size)
        # make sure it's odd
        if size % 2 == 0:
            size += 1
        self.blur_size = size

    def toggle_should_blur(self):
        self.should_blur = not self.should_blur

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
