import unittest

import numpy as np

from utils.geometry import calculate_distance_between, get_contour_center


class TestGeometry(unittest.TestCase):
    def test_get_contour_center(self):
        # square with center (1, 1)
        contour = np.array([[[0, 0]], [[2, 0]], [[2, 2]], [[0, 2]]])
        center = get_contour_center(contour)
        self.assertEqual(center, (1, 1))

    def test_get_zero_area_contour_center(self):
        # contour with zero area
        contour = np.array([[[1, 1]], [[1, 1]], [[1, 1]]])
        center = get_contour_center(contour)
        # should fall back to first point
        self.assertEqual(center, (1, 1))

    def test_calculate_distance_between(self):
        distance = calculate_distance_between((1, 2), (5, 6))
        self.assertAlmostEqual(distance, 5.65685424949, places=10)

    def test_calculate_distance_between_same_point(self):
        distance = calculate_distance_between((1, 2), (1, 2))
        self.assertEqual(distance, 0.0)

    def test_calculate_distance_between_negative_coordinates(self):
        distance = calculate_distance_between((-1, -2), (-5, -6))
        self.assertAlmostEqual(distance, 5.65685424949, places=10)

    def test_calculate_distance_between_float_coordinates(self):
        distance = calculate_distance_between((1.5, 2.5), (5.5, 6.5))
        self.assertAlmostEqual(distance, 5.65685424949, places=10)


if __name__ == "__main__":
    unittest.main()
