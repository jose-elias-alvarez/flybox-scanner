import cv2

# 0 is absolute black, 255 is absolute white
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
            # keep original frame dimensions
            x, y, w, h = (0, 0, frame.shape[1], frame.shape[0])
        return (x, y, w, h)
