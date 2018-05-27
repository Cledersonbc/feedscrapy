#!/usr/bin/env python3
import unittest
from feeds.feedscrapy import Feeder


class TestFeeder(unittest.TestCase):

    def test_invalid_rss(self):
        feeder = Feeder()
        url = 'https://www.invalid_url_rss.invalid'

        with self.assertRaises(Exception):
            feeder.set_rss(url)

    def test_valid_rss(self):
        feeder = Feeder()
        url = 'http://feeds.feedburner.com/PythonInsider'
        feeder.set_rss(url)

    def test_set_max_feed(self):
        feeder = Feeder()
        feeder.set_maxfeed(10)
        self.assertEqual(10, feeder.maxfeed)

    def test_no_words_get_entries(self):
        feeder = Feeder()
        url = 'http://feeds.feedburner.com/PythonInsider'
        keyword_list = []

        feeder.set_rss(url)
        content = feeder.get_entries(keyword_list)
        self.assertEqual(0, len(content))

    def test_with_words_get_entries(self):
        feeder = Feeder()
        url = 'http://feeds.feedburner.com/PythonInsider'
        keyword_list = ['a', 'b']

        feeder.set_rss(url)
        content = feeder.get_entries(keyword_list)
        self.assertGreater(len(content), 0)

    def test_specific_search_get_entries(self):
        # It depends on the feed moment
        feeder = Feeder()
        url = 'http://feeds.feedburner.com/PythonInsider'
        keyword_list = ['pip 10', 'PyPA']

        feeder.set_rss(url)
        content = feeder.get_entries(keyword_list, stype=0)
        self.assertEqual(2, len(content))


if __name__ == '__main__':
    unittest.main()
