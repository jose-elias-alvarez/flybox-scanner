import numpy as np
import cv2
import sys
from create_handler import create_handler

from detect_wells import detect_wells
from create_emitter import create_emitter
from utils import clamp_frame_size, draw_rectangle

TEXT_COLOR = (0, 255, 0)
TRACKER_COLOR = (255, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
VIDEO_SOURCE = "videos/Fly.mp4"
# VIDEO_SOURCE = "videos/DoubleFly.mp4"

BGS_TYPES = ["GMG", "MOG", "MOG2", "KNN", "CNT"]
# choose best one to track small objects like flies
BGS_TYPE = "KNN"


# all of this motion detection stuff is taken straight from the udemy tutorial
# and hasn't really been tested / optimized yet
def getKernel(KERNEL_TYPE):
    if KERNEL_TYPE == "dilation":
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    if KERNEL_TYPE == "opening":
        kernel = np.ones((3, 3), np.uint8)
    if KERNEL_TYPE == "closing":
        kernel = np.ones((3, 3), np.uint8)

    return kernel


def getFilter(img, filter):
    if filter == "closing":
        return cv2.morphologyEx(
            img, cv2.MORPH_CLOSE, getKernel("closing"), iterations=2
        )

    if filter == "opening":
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, getKernel("opening"), iterations=2)

    if filter == "dilation":
        return cv2.dilate(img, getKernel("dilation"), iterations=2)

    if filter == "combine":
        closing = cv2.morphologyEx(
            img, cv2.MORPH_CLOSE, getKernel("closing"), iterations=2
        )
        opening = cv2.morphologyEx(
            closing, cv2.MORPH_OPEN, getKernel("opening"), iterations=2
        )
        dilation = cv2.dilate(opening, getKernel("dilation"), iterations=2)

        return dilation


def getBGSubtractor(BGS_TYPE):
    if BGS_TYPE == "GMG":
        return cv2.bgsegm.createBackgroundSubtractorGMG()
    if BGS_TYPE == "MOG":
        return cv2.bgsegm.createBackgroundSubtractorMOG()
    if BGS_TYPE == "MOG2":
        return cv2.createBackgroundSubtractorMOG2()
    if BGS_TYPE == "KNN":
        return cv2.createBackgroundSubtractorKNN()
    if BGS_TYPE == "CNT":
        return cv2.bgsegm.createBackgroundSubtractorCNT()
    print("Invalid detector")
    sys.exit(1)


cap = cv2.VideoCapture(VIDEO_SOURCE)
# cap = cv2.VideoCapture(0)

bg_subtractor = getBGSubtractor(BGS_TYPE)
minArea = 250


def match_coords(wells, contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]

    # we could make this a bit more efficient by checking the boundaries of each grid / row
    # before checking each well, but I doubt it would make a huge difference
    for i, grid in enumerate(wells):
        for j, row in enumerate(grid):
            for k, well in enumerate(row):
                start_point = well[0]
                end_point = well[1]
                if (
                    start_point[0] <= cx <= end_point[0]
                    and start_point[1] <= cy <= end_point[1]
                ):
                    return (i, j, k, well)


def main():
    wells = detect_wells(VIDEO_SOURCE)
    wells = detect_wells(cap)
    tracks = []
    handler, cancel = create_handler(wells, tracks)
    emitter = create_emitter(wells, handler)

    try:
        while cap.isOpened:
            ok, frame = cap.read()
            if not ok:
                print("Finished processing the video")
                break
            frame = clamp_frame_size(frame)
            frame_count = cap.get(cv2.CAP_PROP_POS_FRAMES)

            bg_mask = bg_subtractor.apply(frame)
            bg_mask = getFilter(bg_mask, "closing")
            bg_mask = cv2.medianBlur(bg_mask, 5)

            (countours, hierarchy) = cv2.findContours(
                bg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for contour in countours:
                coords = match_coords(wells, contour)
                if coords:
                    (i, j, k, well) = coords
                    emitter((i, j, k), contour, frame_count)

            result = cv2.bitwise_and(frame, frame, mask=bg_mask)
            for track in tracks:
                # draw in red
                cv2.circle(frame, track, 1, (0, 0, 255), -1)
            cv2.imshow("Frame", frame)
            cv2.imshow("Mask", result)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                cancel()
                break
    except:
        cancel()
        raise


main()
