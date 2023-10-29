import datetime
import unittest
from queue import SimpleQueue
from threading import Timer
from unittest.mock import MagicMock, mock_open, patch

from handlers.file_interval import DELIMITER, FileIntervalHandler


class TestFileInterval(unittest.TestCase):
    output_path = "tests/fixtures/test_output.txt"
    mock_grid_x = 3
    mock_grid_y = 3
    interval = 10

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
        self.mock_open = mock_open()
        self.patcher = patch("builtins.open", self.mock_open)
        self.patcher.start()

        self.cleanup_queue = SimpleQueue()
        self.error_queue = SimpleQueue()
        self.grid = self.make_mock_grid()
        self.handler = FileIntervalHandler(
            self.grid,
            self.output_path,
            interval=self.interval,
            cleanup_queue=self.cleanup_queue,
            error_queue=self.error_queue,
        )

        # replace with mock to be safe,
        # since real timers are potentially nasty
        self.real_start = self.handler.start
        self.handler.start = MagicMock()

    def tearDown(self):
        self.patcher.stop()
        self.mock_open.reset_mock()

    def test_initial_state(self):
        # should set default values
        self.assertEqual(self.handler.timer, None)
        self.assertEqual(self.handler.filename, self.output_path)
        self.assertEqual(self.handler.interval, self.interval)
        self.assertEqual(self.handler.index, 0)
        self.assertLessEqual(self.handler.last_flush, datetime.datetime.now())
        self.assertEqual(self.cleanup_queue.qsize(), 1)

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

        self.mock_open.assert_called_once_with(self.output_path, "w")
        self.mock_open().write.assert_called_once_with("")

    def test_handle(self):
        # should update distance for item at event coords
        event = MagicMock()
        event.item.coords = (0, 0)
        event.distance = 10

        self.handler.handle(event)

        self.assertEqual(self.handler.distances[(0, 0)], 10)

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
        expected_row_parts = [1, "01 Jan 22", "00:00:00", 1, 1, 0, 0, "Ct", 0, 0]
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
        # reset mock, since it's called once in the constructor
        self.mock_open.reset_mock()
        self.handler.make_row = MagicMock()
        self.handler.make_row.return_value = "test_row"

        self.handler.write_data()

        self.mock_open.assert_called_once_with(self.output_path, "a")
        self.mock_open().write.assert_called_once_with("test_row\n")

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

    def test_flush_error(self):
        self.handler.write_data = MagicMock(side_effect=Exception)
        self.handler.start = MagicMock()

        self.handler.flush()
        self.handler.flush()
        self.handler.flush()

        self.assertEqual(self.error_queue.qsize(), 3)

    # do *not* use real timers unless you hate yourself
    @patch.object(Timer, "start")
    @patch.object(Timer, "__init__", return_value=None)
    def test_start(self, Timer_init, Timer_start):
        self.real_start()

        Timer_init.assert_called_once_with(self.handler.interval, self.handler.flush)
        Timer_start.assert_called_once()

    def test_cancel(self):
        self.handler.timer = MagicMock()

        self.handler.cancel()

        self.handler.timer.cancel.assert_called_once()
