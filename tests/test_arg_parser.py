import argparse
import unittest

from utils.arg_parser import tuning_type


class TestArgParser(unittest.TestCase):
    def test_tuning_type_valid(self):
        self.assertEqual(tuning_type("motion"), "motion")

    def test_tuning_type_invalid(self):
        with self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            "Invalid tuning type: invalid. Valid types are: .*",
        ):
            tuning_type("invalid")
