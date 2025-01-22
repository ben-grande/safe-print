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

    def test_safe_print_strip(self) -> None:
        """
        Test if stripping whitespace characters is disabled.
        """
        cases = [
            (" \n ", " \n "),
            ("\n", "\n"),
            ("a\n", "a\n"),
            ("", ""),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text),
                                 result)


    def test_safe_print_esc(self) -> None:
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
            ("\0", "_"),
            ("\1", "_"),
            ("\u0061", "a"),
            ("\u00D6 or \u00F6", "_ or _"),
            ("Ö or ö", "_ or _"),
            ("\x1b]8;;", "_]8;;"),
            ("\u0061", "a"),
            ("a\x1b]8;;b", "a_]8;;b"),
            ("a\x1b]8;;", "a_]8;;"),
            ("a\x1b] 8;;", "a_] 8;;"),
            ("a\x1b ]8;;", "a_ ]8;;"),
            ("\033", "_"),
            ("\033[", "_["),
            ("\x1b[2K", "_[2K"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text),
                                 result)


    def test_safe_print_color(self) -> None:
        """
        Test with colors.
        """
        cases = [
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[38;5;1m", "\x1b[38;5;1m"),
            ("\x1b[;38;5;1m", "\x1b[;38;5;1m"),
            ("\x1b[0;38;5;1m", "\x1b[0;38;5;1m"),
            ("\x1b[38;5;1;1m", "\x1b[38;5;1;1m"),
            ("\x1b[38;5;1;m", "\x1b[38;5;1;m"),
            ("\x1b[38;2;255;0;1m", "\x1b[38;2;255;0;1m"),
            ("\x1b[38;2;255;0;0;m", "\x1b[38;2;255;0;0;m"),
            ("\x1b[38;2;255;0;0;0m", "\x1b[38;2;255;0;0;0m"),
            ("\x1b[;38;2;255;0;0m", "\x1b[;38;2;255;0;0m"),
            ("\x1b[0;38;2;255;0;0m", "\x1b[0;38;2;255;0;0m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=True,
                                            extra_colors=True),
                                 result)


    def test_safe_print_no_extra_color(self) -> None:
        """
        Test disabling extra colors.
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


    def test_safe_print_no_color(self) -> None:
        """
        Test disabling colors.
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


    def test_safe_print_no_specific_color(self) -> None:
        """
        Test disabling specific colors.
        """
        cases = [
            ("\x1b[30m", "_[30m"),
            ("\x1b[31m", "\x1b[31m"),
            ("\x1b[32m", "\x1b[32m"),
            ("\x1b[37m", "_[37m"),
            ("\x1b[30;1m", "_[30;1m"),
            ("\x1b[0;30m", "_[0;30m"),
            ("\x1b[38;5;30m", "\x1b[38;5;30m"),
            ("\x1b[0;;;30;;;38;5;0m", "_[0;;;30;;;38;5;0m"),
            ("\x1b[38;2;0;30;0m", "\x1b[38;2;0;30;0m"),
            ("\x1b[38;2;0;30;30m", "_[38;2;0;30;30m"),
        ]
        for text, result in cases:
            with self.subTest(text=text, result=result):
                self.assertEqual(safe_print(text, colors=True,
                                            extra_colors=True,
                                            exclude_colors=["30", "37"]),
                                 result)


if __name__ == "__main__":
    unittest.main()
