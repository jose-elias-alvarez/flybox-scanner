import unittest

import cv2

from detection.motion import MotionDetector
from utils.app_settings import AppSettings


class TestMotionDetector(unittest.TestCase):
    def setUp(self):
        self.settings = AppSettings(keep_defaults=True)
        self.detector = MotionDetector(self.settings)

    def test_detect(self):
        # feed 20 real frames to the subtractor to build a model
        for i in range(20):
            frame = cv2.imread(f"tests/fixtures/frames/{i + 1}.jpg")
            self.detector.detect_with_bg_subtractor(frame)

        contours = self.detector.detect_with_bg_subtractor(frame)
        self.assertEqual(len(contours), 39)
