import unittest
from unittest.mock import MagicMock

import cv2

from handlers.frame import FrameHandler
from utils.app_settings import AppSettings


class TestFrameHandler(unittest.TestCase):
    def setUp(self):
        self.window = MagicMock(settings=AppSettings(keep_defaults=True))
        self.handler = MagicMock()
        self.frame_handler = FrameHandler(self.window, self.handler)

    def test_handle(self):
        for i in range(20):
            frame = cv2.imread(f"tests/fixtures/frames/{i + 1}.jpg")
            self.assertIsNotNone(frame)
            self.frame_handler.handle(frame, i + 1)

        # should get called once per frame
        self.assertEqual(self.handler.on_frame.call_count, 20)
        # should get called once per motion event
        self.assertEqual(self.handler.handle.call_count, 84)

        # check first event
        args, _ = self.handler.handle.call_args_list[0]
        event = args[0]
        # emitted on 2nd frame, since the 1st frame can't produce an event
        self.assertEqual(event.point.frame_count, 2)
        self.assertEqual(event.last_point.frame_count, 1)
