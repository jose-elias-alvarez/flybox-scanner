from components.capture_canvas import CaptureCanvas
from components.idle_canvas import IdleCanvas
from components.record_canvas import RecordCanvas
from components.select_webcam_canvas import SelectWebcamCanvas


class StateManager:
    def __init__(self, window):
        self.window = window

    def idle(self):
        self.window.set_canvas(lambda: IdleCanvas(self.window))

    def capture(self):
        self.window.set_canvas(lambda: CaptureCanvas(self.window))

    def select_webcam(self):
        self.window.set_canvas(lambda: SelectWebcamCanvas(self.window))

    # requires using a lambda, not the friendlest but works for now
    def record(self, capture_canvas):
        self.window.set_canvas(lambda: RecordCanvas(self.window, capture_canvas))
