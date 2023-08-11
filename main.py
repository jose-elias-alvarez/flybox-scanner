import cv2
import logging
from detection.frame import crop
from detection.grids import GridDetector
from handlers.debug import debug_handler
from handlers.frame import FrameHandler


def get_frame_generator(cap):
    frame_count = 0
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = crop(frame)
        frame_count += 1
        yield frame, frame_count


def main():
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("videos/DoubleFly.mp4")
    frame_generator = get_frame_generator(cap)

    # in the actual app, we'll have this as a separate step
    # for now, just use the first frame
    first_frame = next(frame_generator)[0]
    grid_detector = GridDetector(first_frame)
    grids, dimensions = grid_detector.detect()

    frame_handler = FrameHandler(grids, dimensions, debug_handler)
    try:
        for frame, frame_count in frame_generator:
            frame_handler.handle(frame, frame_count)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except Exception as e:
        logging.exception(e)
    finally:
        cap.release()
        cv2.destroyAllWindows()


main()
