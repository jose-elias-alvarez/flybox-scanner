from components.idle_canvas import IdleCanvas
from components.record_canvas import RecordCanvas
from components.scan_canvas import ScanCanvas
from components.select_webcam_canvas import SelectWebcamCanvas


class StateManager:
    def __init__(self, window):
        self.window = window

    def idle(self):
        self.window.set_canvas(lambda: IdleCanvas(self.window))

    def scan(self):
        self.window.set_canvas(lambda: ScanCanvas(self.window))

    def select_webcam(self):
        self.window.set_canvas(lambda: SelectWebcamCanvas(self.window))

    # requires using a lambda, not the friendlest but works for now
    def record(self, scan_canvas):
        self.window.set_canvas(lambda: RecordCanvas(self.window, scan_canvas))
