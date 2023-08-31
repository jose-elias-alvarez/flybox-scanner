import unittest

import cv2
import numpy as np

from detection.border import BorderDetector


class TestBorderDetector(unittest.TestCase):
    def setUp(self):
        self.detector = BorderDetector()

    def test_get_border_with_contours(self):
        # black image w/ a white rectangle in the center
        img = np.zeros((300, 300, 3), np.uint8)
        cv2.rectangle(
            img,
            (100, 100),
            (200 - 1, 200 - 1),  # subtract 1 to account for cv2's rectangle drawing
            (255, 255, 255),
            thickness=0,
        )

        border = self.detector.get_border(img)

        self.assertEqual(border, (100, 100, 100, 100))

    def test_get_border_without_contours(self):
        # white image w/ a black rectangle in the center
        img = np.ones((300, 300, 3), np.uint8)
        cv2.rectangle(img, (100, 100), (200, 200), (0, 0, 0), thickness=0)

        border = self.detector.get_border(img)

        # assert that the border is the same as the whole image,
        # i.e. we didn't detect a contour
        self.assertEqual(border, (0, 0, img.shape[1], img.shape[0]))

    def test_get_border_from_frame(self):
        img = cv2.imread("tests/fixtures/frame.jpg")

        border = self.detector.get_border(img)

        self.assertIsNotNone(border)
        (x, y, w, h) = border
        self.assertAlmostEqual(x, 45, delta=5)
        self.assertAlmostEqual(y, 55, delta=5)
        self.assertAlmostEqual(w, 440, delta=5)
        self.assertAlmostEqual(h, 285, delta=5)
