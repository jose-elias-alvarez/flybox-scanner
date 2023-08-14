import cv2

from components.root_window import RootWindow


def main():
    cap = cv2.VideoCapture("videos/DoubleFly.mp4")
    root_window = RootWindow(cap)
    root_window.start()


main()
