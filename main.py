import cv2

from components.main_window import MainWindow


def main():
    cap = cv2.VideoCapture(1)
    window = MainWindow(cap)

    window.start()


main()
