import unittest

import cv2

from detection.grids import (
    GridDetector,
)


class TestGridDetector(unittest.TestCase):
    expected_circles = 96
    expected_rows = 8
    expected_columns = 12
    expected_radius = 20
    expected_area = (20 * 2) ** 2

    def setUp(self):
        self.test_image = cv2.imread("tests/fixtures/grid.jpg")
        self.detector = GridDetector(self.test_image)

    def test_detect(self):
        grid = self.detector.detect()

        self.assertIsNotNone(grid)
        self.assertEqual(len(grid.rows), self.expected_rows)
        for row in grid.rows:
            self.assertEqual(len(row.items), self.expected_columns)

    def test_average_grid_item_size(self):
        grid = self.detector.detect()

        average_area = sum(
            (end_point[0] - start_point[0]) * (end_point[1] - start_point[1])
            for row in grid.rows
            for item in row.items
            for start_point, end_point in [item.bounds]
        ) / (len(grid.rows) * len(grid.rows[0].items))
        self.assertAlmostEqual(average_area, self.expected_area, delta=100)

    def test_detect_circles(self):
        self.detector.processed_frame = self.detector.process_frame()

        circles = self.detector.detect_circles()

        self.assertIsNotNone(circles)
        self.assertEqual(len(circles), self.expected_circles)

    def test_get_approximate_average_radius(self):
        self.detector.processed_frame = self.detector.process_frame()

        radius = self.detector.get_approximate_average_radius()

        self.assertIsNotNone(radius)
        self.assertAlmostEqual(radius, self.expected_radius, places=0)


if __name__ == "__main__":
    unittest.main()
