import cv2

# this class crops a given frame to the area of interest
# this is desriable because it essentially increases the usable area of the video,
# making everything more accurate without increasing processing time

# since the inside of the flybox is dark, we use a simple threshold
# 0 is absolute black, 255 is absolute white
# if the frame is still too large, we can set this to a higher value
# (which should be pretty safe, since the area of interest is so bright)
THRESH = 40


class BorderDetector:
    def get_border(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, THRESH, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if len(contours) > 0:
            cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(cnt)
        else:
            # if we can't detect a border, just use the whole frame
            x, y, w, h = (0, 0, frame.shape[1], frame.shape[0])
        return (x, y, w, h)
