import cv2

from components.root_window import RootWindow


def main():
    cap = cv2.VideoCapture(0)  # default to first camera
    root_window = RootWindow(cap)
    root_window.start()


main()
