#!/usr/bin/env python3

from start import *
import unittest


class TestStart(unittest.TestCase):

    def test_generic_read_item_valid_path(self):
        path = os.path.join('input', 'emails.txt')
        generic_read_item(path)

    def test_generic_read_item_invalid_path(self):
        path = os.path.join('errorput', 'emails.txt')
        with self.assertRaises(Exception):
            generic_read_item(path)

    def test_load_template(self):
        with self.assertRaises(Exception):
            load_template()

    def test_main(self):
        main()


if __name__ == '__main__':
    unittest.main()
