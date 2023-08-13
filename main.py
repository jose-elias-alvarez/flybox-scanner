import logging

import cv2

from detection.frame import crop
from detection.grids import GridDetector
from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler


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
    cap = cv2.VideoCapture("videos/Fly.mp4")
    frame_generator = get_frame_generator(cap)

    # in the actual app, we'll have this as a separate step
    # for now, just use the first frame
    first_frame = next(frame_generator)[0]
    grid_detector = GridDetector(first_frame)
    grid = grid_detector.detect()

    to_file_handler = ToFileHandler(grid)
    resolution_handler = ResolutionHandler(5, to_file_handler)
    resolution_handler.start()

    def wrapped_handler(e):
        resolution_handler.handle(e)
        debug_handler(e)

    frame_handler = FrameHandler(grid, wrapped_handler)
    try:
        for frame, frame_count in frame_generator:
            frame_handler.handle(frame, frame_count)
            if resolution_handler.error is not None:
                raise resolution_handler.error
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except Exception as e:
        logging.exception(e)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        resolution_handler.cancel()


main()
