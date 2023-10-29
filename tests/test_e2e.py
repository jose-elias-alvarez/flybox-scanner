import os
import unittest
from tkinter import TclError
from unittest.mock import MagicMock

from components.root_window import RootWindow


class TestE2E(unittest.TestCase):
    source_file = "tests/fixtures/video.mp4"
    output_file = "tests/test_output.txt"
    totals_file = "tests/fixtures/totals.txt"
    # keep this as False unless parameters change drastically, e.g. if defaults change
    # or if there is a major overhaul to detection in general
    should_update_totals = False

    # the video is 10 seconds long, so 10 lines is what we have
    target_lines = 10
    interval = 1

    expected_dimensions = (8, 12)
    # there is a distressingly high level of non-determinism in our totals,
    # most likely because we're going through Tkinter
    # until we have a better method that skips the UI, keep this high
    delta = 100

    def setUp(self):
        os.environ["SOURCE"] = self.source_file
        os.environ["OUTPUT_FILE"] = self.output_file
        os.environ["INTERVAL"] = str(self.interval)
        self.root_window = RootWindow(args=MagicMock(silent=True, keep_defaults=True))

    def tearDown(self):
        try:
            self.root_window.on_close()
        except TclError:
            # window is already closed
            pass
        try:
            os.remove(self.output_file)
        except FileNotFoundError:
            # file was never created
            pass

    def update_totals(self, actual_totals):
        with open(self.totals_file, "w") as f:
            for total in actual_totals:
                f.write(f"{total}\n")

    def test_e2e(self):
        idle_canvas = self.root_window.children["!idlecanvas"]
        scan_button = idle_canvas.button_frame.children["!button"]
        scan_button.invoke()
        scan_canvas = self.root_window.children["!scancanvas"]
        record_button = scan_canvas.record_button
        record_button.invoke()

        grid = self.root_window.app_state["grid"]
        self.assertEqual(grid.dimensions, self.expected_dimensions)
        self.assertTrue(os.path.exists(self.output_file))
        self.root_window.start()

        with open(self.totals_file, "r") as f:
            totals = [int(line) for line in f.readlines()[: self.target_lines]]
        if not self.should_update_totals:
            self.assertGreaterEqual(
                len(totals),
                self.target_lines,
                "target lines exceeds number of saved totals",
            )

        actual_totals = []
        with open(self.output_file, "r") as f:
            lines = f.readlines()
            self.assertGreaterEqual(len(lines), self.target_lines)
            for i in range(self.target_lines):
                total = sum(int(part) for part in lines[i].split("\t")[8:])
                actual_totals.append(total)

        if self.should_update_totals:
            self.update_totals(actual_totals)
        else:
            for i in range(self.target_lines):
                self.assertAlmostEqual(totals[i], actual_totals[i], delta=self.delta)


if __name__ == "__main__":
    unittest.main()
