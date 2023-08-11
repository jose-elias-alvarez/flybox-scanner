import cv2
import numpy as np

from utils import clamp_frame_size, draw_circle, show_frame

MAX_ITERATIONS = 100
# NOTE: these values are used for circle detection
# and don't correspond to the actual number of wells
MAX_CIRCLES = 96 * 2
# since hough circles is so awful,
# lowering this will lead to more false positives
# and slow down the detection phase
MIN_CIRCLES = 12

CONVERGENCE_THRESHOLD = 0.0005


def get_sample_frame(cap):
    clahe = cv2.createCLAHE(clipLimit=4, tileGridSize=(8, 8))
    ok, sample_frame = cap.read()
    if not ok:
        raise Exception("No frames detected")

    sample_frame = clamp_frame_size(sample_frame)
    processed_frame = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2GRAY)
    processed_frame = clahe.apply(processed_frame)
    # it's recommended to use blurring here,
    # but it seems to make the first detection phase less consistent
    # processed_frame = cv2.GaussianBlur(processed_frame, (5, 5), 0)
    return (processed_frame, sample_frame)


def get_approximate_average_radius(frame, original_frame):
    # use conservative values
    param1 = 40
    param2 = 50
    # we start by assuming that the frame contains at most MAX_CIRCLES
    # and at least MIN_CIRCLES
    max_radius = int(min(frame.shape[0], frame.shape[1]) / MIN_CIRCLES)
    min_radius = int(min(frame.shape[0], frame.shape[1]) / MAX_CIRCLES)
    min_dist = min_radius * 2
    # on each iteration, we update the parameters
    # using the average radius of the circles we detected
    iterations = 0
    # we also keep track of the last average radius so we can exit early
    # once we've converged
    last_average_radius = float("inf")
    while iterations < MAX_ITERATIONS:
        iterations += 1
        detected = cv2.HoughCircles(
            frame,
            cv2.HOUGH_GRADIENT,
            1,
            min_dist,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius,
        )
        if detected is None:
            continue
        average_radius = np.average(detected[0, :, 2])
        # if our new average is (almost) the same as the old average, we're done
        if abs(average_radius - last_average_radius) < CONVERGENCE_THRESHOLD:
            break
        # if our new average is larger than the old average,
        # we most likely have a bad detection,
        # so we ignore it and try again
        if average_radius > last_average_radius * 1.05:  # allow a little flexibility
            continue

        # update values
        min_radius = int(average_radius * 0.5)
        max_radius = int(average_radius * 1.5)
        min_dist = min_radius * 2
        last_average_radius = average_radius

        # draw circles so users don't think the program has frozen
        # (and because it looks cool)
        # we could add a cli flag / gui option to disable this
        copy = original_frame.copy()
        for circle in detected[0]:
            draw_circle(circle, copy, (255, 0, 0))
        show_frame(copy, 75)

    return last_average_radius


def detect_circles(frame, original_frame):
    # TODO: check for infinity
    approximate_average_radius = get_approximate_average_radius(frame, original_frame)
    # now that we have an approximate radius, we can keep our radius tighter
    min_radius = int(approximate_average_radius * 0.85)
    max_radius = int(approximate_average_radius * 1.15)
    min_dist = min_radius * 2
    detected = cv2.HoughCircles(
        frame,
        cv2.HOUGH_GRADIENT,
        1,
        min_dist,
        param1=10,
        param2=20,  # now we can make this looser
        minRadius=min_radius,
        maxRadius=max_radius,
    )
    if detected is None:
        raise Exception("No wells detected")
    circles = detected[0]
    if len(circles) % 2 != 0:
        raise Exception(f"Invalid number of wells detected: {len(circles)}")

    copy = original_frame.copy()
    for circle in detected[0]:
        draw_circle(circle, copy, (0, 255, 0))
    show_frame(copy, 500)

    average_radius = np.average(circles[:, 2])
    # our first goal: convert each detected circle into a well,
    # and sort each well into a box
    boxes = [[]]
    # if a well's x position is too far from the center of the previous well,
    # we'll know we've reached a new box,
    # so we start by sorting by x position
    for x, y, radius in sorted(circles, key=lambda circle: circle[0]):
        # lighting can cause variations beyond what we expect,
        # so we smooth out the radius using a weighted average
        radius = (radius * 0.25) + (average_radius * 0.75)
        # we represent wells as rectangles to make motion detection easier
        # and avoid (literal) edge cases
        well = (
            (
                x - radius,
                y - radius,
            ),
            (
                x + radius,
                y + radius,
            ),
        )
        # case 1: no wells in box, so we can't make a comparison
        last_box = boxes[-1]
        if len(last_box) == 0:
            last_box.append(well)
            continue
        # case 2: well is too far from last well on the x axis, so we're in a new box
        last_well = last_box[-1]
        distance = well[1][0] - last_well[1][0]
        # this is sort of arbitrary and could need tweaking depending on actual box dimensions
        is_new_box = distance > average_radius * 2.5
        if is_new_box:
            boxes.append([well])
            continue
        # case 3: well is close enough to last well, so we're still in the same box
        last_box.append(well)

    # our next goal is to organize each box into rows
    for i, box in enumerate(boxes):
        # this time we'll use the y position to determine if we're in a new row
        box.sort(key=lambda well: well[0][1])
        box_by_row = [[]]
        for well in box:
            # case 1: no wells in row, so we can't make a comparison
            row = box_by_row[-1]
            if len(row) == 0:
                row.append(well)
                continue
            # case 2: well is too far from last well on the y axis, so we're in a new row
            last_well = row[-1]
            distance = well[1][1] - last_well[1][1]
            is_new_row = distance > average_radius
            if is_new_row:
                box_by_row.append([well])
                continue
            # case 3: well is close enough to last well, so we're still in the same row
            row.append(well)
        boxes[i] = box_by_row

    # finally, we peform some basic validation and sort each row by x position
    for box in boxes:
        # validate that each box contains the same number of rows
        if len(box) != len(boxes[0]):
            raise Exception(
                f"Invalid number of rows (expected {len(boxes[0])}, got {len(box)})"
            )
        for row in box:
            if len(row) != len(box[0]):
                raise Exception(
                    f"Invalid number of wells in row (expected {len(box[0])}, got {len(row)})"
                )
            row.sort(key=lambda well: well[0])
    return boxes


def detect_wells(cap):
    (frame, original_frame) = get_sample_frame(cap)
    boxes = detect_circles(frame, original_frame)

    # light variable naming inconsistency
    return boxes
