import cv2
import numpy as np

# this class is responsible for detecting motion in a frame

# the motion detector uses a background subtractor to detect motion
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

# this is a closing operation,
# which means it effectively "fills in" holes in the detected motion
# this seems to work best for our case but could definitely benefit from tuning
OPERATION = cv2.MORPH_CLOSE
# more iterations = more closing
ITERATIONS = 3

# blurring the image before detecting motion helps to reduce noise
SHOULD_BLUR = True
BLUR_SIZE = 5


class MotionDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
            history=HISTORY, dist2Threshold=DIST2_THRESHOLD, detectShadows=False
        )
        self.kernel = np.ones(KERNEL_SIZE, np.uint8)

    def get_bg_mask(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray)
        mask = cv2.morphologyEx(mask, OPERATION, self.kernel, iterations=ITERATIONS)
        if SHOULD_BLUR:
            mask = cv2.medianBlur(mask, BLUR_SIZE)
        return mask

    def get_center(self, contour):
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return
        x = M["m10"] / M["m00"]
        y = M["m01"] / M["m00"]
        return (x, y)

    def detect(self, frame):
        bg_mask = self.get_bg_mask(frame)
        (contours, _) = cv2.findContours(
            bg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
