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


# this is not really suitable for production use
boundary = None


def crop(frame):
    global boundary
    if boundary is None:
        # convert the image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # threshold the image to get non-black pixels
        _, threshold = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

        # use opencv findContours to get bounding box of the non-black region
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnt = max(contours, key=cv2.contourArea)  # get the largest contour
        x, y, w, h = cv2.boundingRect(cnt)
        boundary = (x, y, w, h)
    else:
        (x, y, w, h) = boundary

    frame = frame[y : y + h, x : x + w]
    return frame


# the default width and height here provide good results on our sample videos
# but need to be tested on actual lab hardware
def clamp_frame_size(frame, max_width=640, max_height=480):
    frame = crop(frame)
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
