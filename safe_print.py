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

def safe_print(text: str, colors=True, extended_colors=True) -> str:
    """
    Safely print the text passed as argument based in the allow list:
      - Printable ASCII + newline + tab
      - ANSI 4-bit SGR
    """
    output = []
    length = len(text)

    allowed_space = {ord("\n"), ord("\t")}
    ## Warning: text is concealed if fg color is the same as terminal bg color.
    ## TODO: verify which attributes should stay.
    ## SGR 4-bit: (;*<format>(;<format>)*m|m)
    ## SGR 8-bit: ((<4bit>;+)?[3-4]8;5;<0-255>m)
    ## SGR 24-bit: ((<4bit>;+)?[3-4]8;2;<0-255>;<0-255>;<0-255>m)
    if colors:
        sgr_4bit = r"([0-9]|2[1-5]|2[7-9]|3[0-7]|39|4[0-7]|49|9[0-7]|10[0-7])"
        sgr_4bit = rf";*{sgr_4bit}(;{sgr_4bit})*"
        sgr_re = rf"(;*|{sgr_4bit})?m"
        if extended_colors:
            eight_bit = r"([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
            sgr_8bit = rf"[3-4]8;5;{eight_bit}"
            sgr_24bit = rf"[3-4]8;2;{eight_bit};{eight_bit};{eight_bit}"
            sgr_re = rf"{sgr_re}|({sgr_4bit};+)*({sgr_8bit}|{sgr_24bit})m"
        sgr_pattern = re.compile(sgr_re)

    i = 0
    while i < length:
        char = text[i]
        hex_value = ord(char)
        if 0x20 <= hex_value <= 0x7e or hex_value in allowed_space:
            output.append(char)
        elif colors and hex_value == 0x1b and text[i + 1] == "[":
            ## Sanitize CSI sequence
            sgr_match = re.match(sgr_pattern, text[i + 2:])
            if sgr_match:
                sgr_match_length = sgr_match.end()
                output.append(text[i:i + 2 + sgr_match_length])
                i += sgr_match_length + 1
            else:
                ## Sanitize prohibited CSI sequence
                output.append("_")
        else:
            ## Sanitize prohibited character
            output.append("_")
        i += 1

    return "".join(output)


def main():
    """
    Read text input and sanitize it.
    You may pass from the terminal:
      safe_print.py "$(printf '%b\n' "untrusted_string\033[2K")"
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs=argparse.REMAINDER, help="text to print safely")
    args = parser.parse_args()
    text = "\n".join(args.text)
    ## TODO: delete raw text print, dangerous and only useful for debugging. Remove
    ## when unit tests are made.
    #print(text)
    print(safe_print(text))


if __name__ == "__main__":
    main()
