#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
##
## SPDX-License-Identifier: TODO

## https://en.wikipedia.org/wiki/ANSI_escape_code#SGR

"""
Sanitize text to only print ASCII and a subset of ANSI SGR
"""

import argparse
import re

def safe_print(text):
    """
    Safely print the text passed as argument based in the allow list:
      - Printable ASCII + newline + tab
      - ANSI 4-bit SGR
    """
    output = ""
    allowed_space = [ord("\n"), ord("\t")]
    ## Warning: if foreground color is the same as terminal background color,
    ## the text will be hidden.
    ## TODO: verify which attributes should stay.
    ## SGR 4-bit: (;*<format>m|;*<format>(;<format>)*<color>m)
    sgr_pattern = r"([0-9]|2[1-5]|2[7-9]|3[0-7]|39|4[0-7]|49|9[0-7]|10[0-7])"
    sgr_pattern = rf";?{sgr_pattern}(;{sgr_pattern})*m"
    sgr_pattern = re.compile(sgr_pattern)
    ## SGR 8-bit: [3-4]8;5;[0-255]m
    ## SGR 24-bit [3-4]8;2;[0-255];[0-255];[0-255]m

    i = 0
    while i < len(text):
        char = text[i]
        hex_value = ord(char)

        if 0x20 <= hex_value <= 0x7e or hex_value in allowed_space:
            output += char
        elif char == "]":
            ## Sanitize OSC
            output += "_"
        elif hex_value == 0x1b:
            if i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == "[":
                    sgr_match = re.match(sgr_pattern, text[i+2:])
                    if sgr_match:
                        sgr_match_length = sgr_match.span()[1]
                        output += text[i:i+2+sgr_match_length]
                        i += sgr_match_length + 1
                    else:
                        ## Sanitize prohibited ANSI control sequence
                        output += "_"
                else:
                    ## Skip ESC without CSI (C0 control code)
                    pass
            else:
                ## Skip ESC that is at the end of the text
                pass
        else:
            ## Sanitize prohibited character
            output += "_"
        i += 1

    return output


def main():
    """
    Read text input and sanitize it.
    """
    ## TODO: fix: args.input is passed as a raw string instead of f-string.
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs=argparse.REMAINDER, help="text to print safely")
    args = parser.parse_args()
    text = "\n".join(args.text)

    ## Comment this line to test argument passed from the command line.
    text = "Öoö \x1b[61mFramed\033[0;34mBlue\x1b[0mReset\x1b[2K"

    ## TODO: delete raw text print, dangerous and only useful for debugging
    print(text)
    print(safe_print(text))


if __name__ == "__main__":
    main()
