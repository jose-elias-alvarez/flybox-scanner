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

    to_file_handler = None
    resolution_handler = None
    frame_handler = None
    grid = None

    def wrapped_handler(e):
        if resolution_handler is not None:
            resolution_handler.handle(e)
        debug_handler(e)

    def capture_frame():
        global paused
        nonlocal captured_img_tk, captured_img_id
        nonlocal grid

        frame = next(get_frame_generator(cap))[0]
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
        nonlocal to_file_handler, resolution_handler, frame_handler
        nonlocal grid
        to_file_handler = ToFileHandler(grid)
        resolution_handler = ResolutionHandler(5, to_file_handler)
        frame_handler = FrameHandler(grid, wrapped_handler)
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

    img = None
    img_id = None

    generator = get_frame_generator(cap)

    def update_frame():
        global paused, hide
        nonlocal img, img_id
        if not paused:
            frame, frame_count = next(generator)
            if resolution_handler is not None and not resolution_handler.started:
                resolution_handler.start()
            if frame_handler is not None:
                frame_handler.handle(frame, frame_count)
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
