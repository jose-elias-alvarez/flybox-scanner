from threading import Timer
import time


class ResolutionHandler:
    def __init__(self, resolution, handler):
        self.resolution = resolution
        self.handler = handler

        self.last_flush = time.time()
        self.error = None

    def start(self):
        self.timer = Timer(self.resolution, self.flush)
        self.timer.start()

    def flush(self):
        now = time.time()
        # print(f"Delta: {now - self.last_flush}")
        self.last_flush = now
        try:
            self.handler.on_flush(now)
            self.start()
        except Exception as e:
            self.error = e

    def cancel(self):
        self.timer.cancel()

    def handle(self, event):
        self.handler.on_event(event)
