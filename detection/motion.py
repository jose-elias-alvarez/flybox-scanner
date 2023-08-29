import cv2
import numpy as np

# this class is responsible for detecting motion in a frame
# at the moment, it supports two methods:
# 1. background subtraction
# 2. frame differencing (experimental, not recommended)

METHOD = "BG_SUBTRACTOR"

# this parameter is the number of frames to keep in the background subtractor
# the higher the number, the more motion is required to trigger a detection
# this is good for our case but will cause slower updates if there is any motion
# (e.g. if the camera is moved or if it needs to refocus)
HISTORY = 1000

# this parameter is the distance threshold for the background subtractor
# the higher the number, the more motion is required to trigger a detection
DIST2_THRESHOLD = 200

# this parameter is the kernel size for the morphological operations
# a larger kernel size will cause the detected motion to be larger,
# which is not really what we want
KERNEL_SIZE = (3, 3)

# blurring the image before subtracting seems to help reduce noise
SHOULD_BLUR = True
BLUR_SIZE = 5

# we can also use a simple frame differencing method,
# where we compare each frame to the previous frame
# this is theoretically the most sensitive method,
# but the resulting motion is much jerkier,
# so this requires more tuning before we can use it
# METHOD = "DIFF"

# threshold used to determine if a pixel is part of the motion
# any lower than this and we start to get weird light artifacts
DIFF_THRESHOLD = 15


class MotionDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=HISTORY, dist2Threshold=DIST2_THRESHOLD, detectShadows=False
        )
        self.kernel = np.ones(KERNEL_SIZE, np.uint8)
        self.last_frame = None

    def get_bg_mask(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        # this is a closing operation,
        # which means it effectively "fills in" holes in the detected motion
        # this seems to work best for our case but could definitely benefit from tuning
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            self.kernel,
            iterations=3,  # more iterations = more closing
        )
        if SHOULD_BLUR:
            mask = cv2.medianBlur(mask, BLUR_SIZE)
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
        thresh = cv2.dilate(thresh, None, iterations=2)

        self.last_frame = frame.copy()
        return self.find_contours(thresh)

    def detect(self, frame):
        if METHOD == "BG_SUBTRACTOR":
            return self.detect_with_bg_subtractor(frame)
        elif METHOD == "DIFF":
            return self.detect_with_diff(frame)
        else:
            raise Exception(f"Invalid method: {METHOD}")
