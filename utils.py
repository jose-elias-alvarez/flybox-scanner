import cv2


def draw_circle(circle, frame, color=(0, 255, 0)):
    center = (int(circle[0]), int(circle[1]))
    radius = int(circle[2])
    cv2.circle(
        frame,
        center,
        radius,
        color,
        2,
    )


def draw_rectangle(rectangle, frame, color=(0, 255, 0)):
    start_point = (int(rectangle[0][0]), int(rectangle[0][1]))
    end_point = (int(rectangle[1][0]), int(rectangle[1][1]))
    cv2.rectangle(
        frame,
        start_point,
        end_point,
        color,
        1,
    )


def show_frame(frame, delay=0):
    cv2.imshow("Frame", frame)
    cv2.waitKey(delay)


# the default width and height here provide good results on our sample videos
# but need to be tested on actual lab hardware
def clamp_frame_size(frame, max_width=640, max_height=480):
    original_height, original_width = frame.shape[:2]
    aspect_ratio = original_width / original_height

    if (max_width / aspect_ratio) > max_height:
        new_width = int(max_height * aspect_ratio)
        new_height = max_height
    else:
        new_height = int(max_width / aspect_ratio)
        new_width = max_width

    resized = cv2.resize(frame, (new_width, new_height))
    return resized
