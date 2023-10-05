import cv2


def get_webcams(first_available=False):
    index = 0
    webcams = []
    while index < 10:
        cap = cv2.VideoCapture()
        cap.open(index)
        if cap.read()[0]:
            webcams.append(index)
            if first_available:
                return webcams
        cap.release()
        index += 1
    return webcams
