import cv2
import numpy as np


def get_contour_center(contour):
    M = cv2.moments(contour)
    try:
        cX = M["m10"] / M["m00"]
        cY = M["m01"] / M["m00"]
    except ZeroDivisionError:
        return None
    return (cX, cY)


def calculate_distance_between(point1, point2):
    cX1, cY1 = point1[0], point1[1]
    cX2, cY2 = point2[0], point2[1]
    return np.sqrt((cX2 - cX1) ** 2 + (cY2 - cY1) ** 2)
