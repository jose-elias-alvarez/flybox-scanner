import cv2


def draw_circle(circle, frame, color=(0, 255, 0), width=2):
    center = (int(circle[0]), int(circle[1]))
    radius = int(circle[2])
    cv2.circle(frame, center, radius, color, width)


def draw_rectangle(rectangle, frame, color=(0, 255, 0), width=2):
    start_point = (int(rectangle[0][0]), int(rectangle[0][1]))
    end_point = (int(rectangle[1][0]), int(rectangle[1][1]))
    cv2.rectangle(frame, start_point, end_point, color, width)


def draw_contour(contour, frame, color=(0, 255, 0), width=2):
    cv2.drawContours(frame, [contour], -1, color, width)


def show_frame(frame, delay=0):
    cv2.imshow("Frame", frame)
    cv2.waitKey(delay)
