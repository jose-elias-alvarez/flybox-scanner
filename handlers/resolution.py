import time
from queue import Queue
from threading import Timer

from handlers.frame import MotionEvent, MotionHandler


class ResolutionHandler:
    def __init__(self, resolution: int, handler: MotionHandler, error_queue: Queue):
        self.resolution = resolution
        self.handler = handler

        self.last_flush = time.time()
        self.error_queue = error_queue
        self.started = False

    def start(self):
        self.started = True
        self.timer = Timer(self.resolution, self.flush)
        self.timer.start()

    def flush(self):
        timestamp = time.time()
        self.last_flush = timestamp
        try:
            self.handler.on_flush(timestamp)
            self.start()
        except Exception as e:
            self.error_queue.put(e)

    def cancel(self):
        self.timer.cancel()

    def handle(self, event: MotionEvent):
        self.handler.on_event(event)
