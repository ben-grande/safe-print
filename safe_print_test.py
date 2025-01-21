#!/usr/bin/env python3
"""
Test the safe_print module.
"""

import unittest
from safe_print import safe_print


class TestSafePrint(unittest.TestCase):
    """
    Test safe print
    """


    def test_safe_print_esc(self):
        """
        Test ESC sequence
        """
        cases = [
            ("\a", "_"),
            ("\b", "_"),
            ("\t", "\t"),
            ("\n", "\n"),
            ("\v", "_"),
            ("\f", "_"),
            ("\r", "_"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text),
                                 result)


    def test_safe_print_osc(self):
        """
        Test OSC sequence
        """
        cases = [
            ("\x1b]8;;", "_]8;;"),
            ("a\x1b]8;;b", "a_]8;;b"),
            ("a\x1b]8;;", "a_]8;;"),
            ("a\x1b] 8;;", "a_] 8;;"),
            ("a\x1b ]8;;", "a_ ]8;;"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text),
                                 result)


    def test_safe_print_color(self):
        """
        Test with colors
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[38;5;1m", "\x1b[38;5;1m"),
            ("\x1b[38;2;255;0;0m", "\x1b[38;2;255;0;0m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=True,
                                            extra_colors=True),
                                 result)


    def test_safe_print_no_extra_color(self):
        """
        Test disabling extra colors
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=True,
                                            extra_colors=False),
                                 result)


    def test_safe_print_no_color(self):
        """
        Test disabling colors
        """
        cases = [
            ("\x1b[31m", "_[31m"),
            ("\x1b[38;5;1m", "_[38;5;1m"),
            ("\x1b[38;2;255;0;0m", "_[38;2;255;0;0m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=False,
                                            extra_colors=True),
                                 result)


    def test_safe_print_no_specific_color(self):
        """
        Test disabling specific colors
        """
        cases = [
            ("\x1b[30m", "_[30m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[32m", "\x1b[32m"),
            ("\x1b[37m", "_[37m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=True,
                                            extra_colors=True,
                                            exclude_colors=["30", "37"]),
                                 result)


if __name__ == "__main__":
    unittest.main()
