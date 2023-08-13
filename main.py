import queue
import threading
import tkinter as tk

import cv2
from PIL import Image, ImageTk

from detection.frame import crop
from detection.grids import GridDetector
from handlers.debug import debug_handler
from handlers.frame import FrameHandler
from handlers.resolution import ResolutionHandler
from handlers.to_file import ToFileHandler

paused = False
hide = False


class FrameFetcher(threading.Thread):
    def __init__(self, generator):
        super().__init__(daemon=True)
        self.raw_frames = queue.Queue(maxsize=1)
        self.generator = generator

    def run(self):
        global paused
        if paused:
            return
        for frame, frame_count in self.generator:
            self.raw_frames.put((frame, frame_count))


class FrameProcessor(threading.Thread):
    def __init__(self, fetcher):
        super().__init__(daemon=True)
        self.processed_frames = queue.Queue(maxsize=1)
        self.fetcher = fetcher
        self.handler = None

    def run(self):
        while True:
            if not self.fetcher.raw_frames.empty():
                (raw_frame, frame_count) = self.fetcher.raw_frames.get()
                if self.handler is not None:
                    processed_frame = self.handler.handle(raw_frame, frame_count)
                else:
                    processed_frame = raw_frame
                self.processed_frames.put((processed_frame, frame_count))


def main():
    def get_frame_generator(cap):
        frame_count = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = crop(frame)
            frame_count += 1
            yield frame, frame_count

    cap = cv2.VideoCapture("videos/Fly.mp4")

    window = tk.Tk()
    window.title("Webcam Capture")

    # initialize to first frame size
    first_frame = next(get_frame_generator(cap))[0]
    canvas = tk.Canvas(window, width=first_frame.shape[1], height=first_frame.shape[0])
    canvas.pack()

    captured_img_tk = None
    captured_img_id = None

    grid = None

    def capture_frame():
        global paused
        nonlocal captured_img_tk, captured_img_id
        nonlocal grid

        if not frame_processor.processed_frames.empty():
            (frame, _) = frame_processor.processed_frames.get()
            grid_detector = GridDetector(frame)
            grid = grid_detector.detect()

            # Then, display the frame in a new window
            paused = True
            captured_img_tk = ImageTk.PhotoImage(
                image=Image.fromarray(frame)
            )  # Replace frame with processed_frame if you make processed_frame
            if captured_img_id is None:
                captured_img_id = canvas.create_image(
                    0, 0, anchor=tk.NW, image=captured_img_tk
                )
            else:
                canvas.itemconfig(captured_img_id, image=captured_img_tk)

    button = tk.Button(window, text="Capture", command=capture_frame)
    button.pack()

    def resume_stream():
        global paused
        paused = False

    def accept_frame():
        nonlocal grid, frame_processor
        to_file_handler = ToFileHandler(grid)
        resolution_handler = ResolutionHandler(5, to_file_handler)
        resolution_handler.start()

        def wrapped_handler(e):
            resolution_handler.handle(e)
            debug_handler(e)

        frame_handler = FrameHandler(grid, wrapped_handler)
        frame_processor.handler = frame_handler
        resume_stream()

        # destroy captured image
        nonlocal captured_img_id
        if captured_img_id is not None:
            canvas.delete(captured_img_id)
            captured_img_id = None

    ok_button = tk.Button(window, text="OK", command=accept_frame)
    ok_button.pack()

    def hide_frame():
        global hide
        hide = not hide

    hide_button = tk.Button(window, text="Hide", command=hide_frame)
    hide_button.pack()

    frame_fetcher = FrameFetcher(get_frame_generator(cap))
    frame_fetcher.start()

    frame_processor = FrameProcessor(frame_fetcher)
    frame_processor.start()

    img = None
    img_id = None

    def update_frame():
        global paused, hide
        nonlocal img, img_id
        if not paused and not frame_processor.processed_frames.empty():
            (frame, frame_count) = frame_processor.processed_frames.get()
            if not hide:
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                img_id = canvas.create_image(0, 0, anchor=tk.NW, image=img)
            else:
                if img_id is not None:
                    canvas.delete(img_id)
                    img_id = None

        window.after(33, update_frame)

    update_frame()
    window.mainloop()


main()
