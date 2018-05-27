#!/usr/bin/env python3
import unittest
from feeds.feedmail import SMTPServer, Email


class TestSMTPServer(unittest.TestCase):

    def test_server_error(self):
        server = SMTPServer(
            'smtp.invalid.server',
            '587',
            'user',
            'password'
        )

        with self.assertRaises(Exception):
            server.send(Email())


if __name__ == '__main__':
    unittest.main()
