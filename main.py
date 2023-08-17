import cv2

from components.root_window import RootWindow

# main entrypoint for the program
# in the future, we could use something like this to package it into an executable:
# https://pyinstaller.org/en/stable/

WINDOW_TITLE = "Flybox Scanner"
RESIZABLE = False
# this is the delay for the main loop, which determines how often we fetch and process frames
# for videos, a value of 30 roughly equates to 30 fps
# if low fps is causing issues with camera input, we might need to set this independently depending on the source
DELAY = 30
# these dimensions are also used to resize frames
# bigger frames provide more accurate detection but are far slower to process
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

DEFAULT_SOURCE = 0  # first webcam


def main():
    cap = cv2.VideoCapture()
    cap.open(DEFAULT_SOURCE)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    root_window = RootWindow(
        cap,
        title=WINDOW_TITLE,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        delay=DELAY,
        resizable=RESIZABLE,
    )
    root_window.start()


main()
