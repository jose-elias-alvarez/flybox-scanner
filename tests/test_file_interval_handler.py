import datetime
import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

from handlers.file_interval import DEFAULT_INTERVAL, DELIMITER, FileIntervalHandler


class TestFileInterval(unittest.TestCase):
    output_path = "tests/fixtures/test_output.txt"
    mock_grid_x = 3
    mock_grid_y = 3

    def make_mock_grid(self):
        mock_grid = MagicMock()
        mock_grid.rows = []
        for i in range(self.mock_grid_x):
            mock_row = MagicMock()
            mock_row.items = []
            for j in range(self.mock_grid_y):
                mock_item = MagicMock()
                mock_item.coords = (i, j)
                mock_row.items.append(mock_item)
            mock_grid.rows.append(mock_row)
        return mock_grid

    def setUp(self):
        mock_window = MagicMock()
        mock_window.app_state = {"grid": self.make_mock_grid()}

        self.handler = FileIntervalHandler(mock_window, self.output_path)

    def tearDown(self):
        os.remove(self.output_path)
        if self.handler.timer:
            self.handler.timer.cancel()

    def test_initial_state(self):
        # should set default values
        self.assertEqual(self.handler.timer, None)
        self.assertEqual(self.handler.filename, self.output_path)
        self.assertEqual(self.handler.interval, DEFAULT_INTERVAL)
        self.assertEqual(self.handler.index, 0)
        self.assertLessEqual(self.handler.last_flush, datetime.datetime.now())

        # should set distances from grid dimensions, initialized to 0
        expected_distances = {
            (0, 0): 0,
            (0, 1): 0,
            (1, 0): 0,
            (1, 1): 0,
            (2, 0): 0,
            (2, 1): 0,
            (0, 2): 0,
            (1, 2): 0,
            (2, 2): 0,
        }
        self.assertEqual(self.handler.distances, expected_distances)
        self.assertEqual(self.handler.max_x, 2)
        self.assertEqual(self.handler.max_y, 2)

        # should write empty file to output path
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, "r") as f:
            self.assertEqual(f.read(), "")

    def test_handle(self):
        # should update distance for item at event coords
        event = MagicMock()
        event.item.coords = (0, 0)
        event.distance = 10

        self.handler.handle(event)

        self.assertEqual(self.handler.distances[(0, 0)], 10)

    def test_format_time(self):
        # should format time according to format
        dt = datetime.datetime(2022, 1, 1, 0, 0, 0)
        self.assertEqual(self.handler.format_time(dt), "12:00:00")

        # should remove leading 0 from hour
        dt = datetime.datetime(2022, 1, 1, 1, 0, 0)
        self.assertEqual(self.handler.format_time(dt), "1:00:00")

    def test_make_row(self):
        # should return a row string of metadata followed by distances
        self.handler.index = 1
        self.handler.last_flush = datetime.datetime(2022, 1, 1, 0, 0, 0)
        index = 1
        for i in range(3):
            for j in range(3):
                self.handler.distances[(i, j)] = index
                index += 1
        # distances should now look like this:
        # 1 2 3
        # 4 5 6
        # 7 8 9
        expected_row_parts = [
            1,
            "01-Jan-22",
            "12:00:00",
            1,
            1,
            0,
            0,
            0,
            0,
            "Ct",
            0,
        ]
        # go down each column, then move to the next row
        expected_distances = [
            1,
            4,
            7,
            2,
            5,
            8,
            3,
            6,
            9,
        ]
        expected_row_parts += expected_distances
        expected_row = DELIMITER.join(map(str, expected_row_parts))

        row = self.handler.make_row()

        self.assertEqual(row, expected_row)

    def test_write_data(self):
        # should write row to file
        self.handler.make_row = MagicMock()
        self.handler.make_row.return_value = "test_row"

        self.handler.write_data()

        with open(self.output_path, "r") as f:
            self.assertEqual(f.read(), "test_row\n")

    def test_flush(self):
        self.handler.index = 1
        self.handler.distances[(0, 0)] = 100
        self.handler.write_data = MagicMock()
        self.handler.start = MagicMock()

        self.handler.flush()

        self.assertEqual(self.handler.index, 2)
        self.assertLessEqual(self.handler.last_flush, datetime.datetime.now())
        self.handler.write_data.assert_called_once()
        self.handler.start.assert_called_once()
        # should be reset back to 0
        self.assertEqual(self.handler.distances[(0, 0)], 0)

    def test_start(self):
        self.handler.interval = 0.01
        self.handler.flush = MagicMock()

        self.handler.start()
        # max 1 second wait
        # SURELY using real timers here won't come back to bite me
        timeout = time.time() + 1
        while time.time() < timeout:
            if self.handler.flush.call_count > 0:
                break
            time.sleep(0.01)

        self.handler.flush.assert_called_once()
