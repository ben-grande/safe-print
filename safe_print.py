#!/usr/bin/env python3

## SPDX-FileCopyrightText: 2025 Benjamin Grande M. S. <ben.grande.b@gmail.com>
##
## SPDX-License-Identifier: TODO

"""
Sanitize text to be safely printed on the terminal.
"""

import argparse
import re
from typing import Optional, Pattern


def exclude_pattern(original_pattern: str,
                    negate_pattern: list[str]) -> str:
    """Exclude matching next expression if provided expression matches.

    Parameters
    ----------
    original_pattern : str
        Pattern which contains unwanted matches.

    negate_pattern : list[str]
        Pattern to exclude from the next match.

    Returns
    -------
        str: regular expression with negative lookahead

    Examples
    --------
    Redact unsafe sequences by default:
    >>> color_pattern = exclude_pattern(r"(30|31)", ["31"])
    '(?!(?:31))(30|31)'
    """

    exclude_pattern_str = "|".join(map(re.escape, negate_pattern))
    exclude_pattern_str = rf"(?!(?:{exclude_pattern_str}))"
    return rf"{exclude_pattern_str}{original_pattern}"


def get_color_pattern(extra_colors: Optional[bool],
                      exclude_colors: Optional[list[str]]
                      ) -> Pattern[str]:
    """Print compiled RegEx for SGR sequences

    The SGR implementation is well documented[1][2][3] but the overall
    structure of escape sequences syntax isn't, they have a permissive syntax
    and that part is not well documented, assumptions were made based on tests
    using XTerm.

    *   For a CSI sequence to be considered SGR, it must end with "m" and in
        between have zero or more integers and semicolons.
    *   Invalid SGR will lead to one of the following behaviours
        *   Invalidate the whole sequence skipping all SGR.
        *   Invalidate only itself, skipping evaluation of that specific SGR.
    *   Specifying a fg or bg color multiple times will print only the last
        color definition.
    *   Specifying an attribute multiple times will combine them unless they
        revert each other.

    With the definitions above, we set the following pseudo regex:

    -  4-bit SGR: (;*#(;#)*)?m
    -  8-bit SGR: (4-bit;+)?[3-4]8;5;<0-255>(;+4-bit)*m
    - 24-bit SGR: (4-bit;+)?[3-4]8;2;<0-255>;<0-255>;<0-255>(;+4-bit)*m

    Parameters
    ----------
    extra_colors : Optional[bool]
        Whether to allow extra colors or not.
    exclude_colors : Optional[list[str]]
        Color codes to be excluded.

    Returns
    -------
        str: compiled regular expression with negative lookahead

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/ANSI_escape_code
    .. [2] https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    .. [3] https://man.archlinux.org/man/console_codes.4.en.txt

    Examples
    --------
    Redact unsafe sequences by default:
    >>> color_pattern = exclude_pattern(r"(3[0-7])", ["30"])
    '(?!(?:31))3[0-7]'
    """

    ## TODO: verify which attributes should stay.
    sgr_4bit = r"([0-9]|2[1-5]|2[7-9]|3[0-7]|39|4[0-7]|49|9[0-7]|10[0-7])"
    if exclude_colors:
        sgr_4bit = exclude_pattern(sgr_4bit, exclude_colors)
    sgr_4bit = rf";*{sgr_4bit}(;{sgr_4bit})*"
    sgr_re = rf"(;*|{sgr_4bit})?m"
    if extra_colors:
        eight_bit = r"([0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        sgr_8bit = rf"[3-4]8;5;{eight_bit}"
        sgr_24bit = rf"[3-4]8;2;{eight_bit};{eight_bit};{eight_bit}"
        sgr_extra = rf"({sgr_8bit}|{sgr_24bit})"
        if exclude_colors:
            sgr_extra = exclude_pattern(sgr_extra, exclude_colors)
        sgr_re = rf"{sgr_re}|({sgr_4bit};+)*;*{sgr_extra};*(;+{sgr_4bit})*m"
    return re.compile(sgr_re)


def safe_print(untrusted_text: str,
               colors: Optional[bool] = True,
               extra_colors: Optional[bool] = True,
               exclude_colors: Optional[list[str]] = None,
               ) -> str:
    """Sanitize untrusted text to be printed to the terminal.

    Safely print the text passed as argument based in an allow list, allowing
    print printable ASCII, newline, tab and a subset of SGR (color and
    formatting codes).

    Parameters
    ----------
    untrusted_text : str
        The unsafe text to be sanitized.
    colors : Optional[bool] = True
        Whether to allow colors or not.
    extra_colors : Optional[bool] = True
        Whether to allow extra colors or not.
    exclude_colors : Optional[list[str]] = None
        Color codes to be excluded.

    Returns
    -------
        str: sanitized text

    Examples
    --------
    Redact unsafe sequences by default:
    >>> safe_print("\x1b[2Jvulnerable: True\b\b\b\bFalse")
    _[2Jvulnerable: True____False

    Redact all colors:
    >>> safe_print("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", colors=False)
    _[38;5;0m_[31m_[38;2;0;0;0m

    Allow colors but not extra colors bigger than 4bit:
    >>> safe_print("\x1b[38;5;0m\x1b[31m\x1b[38;2;0;0;0m", colors=True,
    ...            extra_colors=False)
    _[38;5;0m\x1b[31m_[38;2;0;0;0m
    """

    allowed_space = {ord("\n"), ord("\t")}
    if colors:
        sgr_pattern = get_color_pattern(extra_colors=extra_colors,
                                        exclude_colors=exclude_colors)
    output = []
    length = len(untrusted_text)
    i = 0
    while i < length:
        char = untrusted_text[i]
        hex_value = ord(char)
        if 0x20 <= hex_value <= 0x7e or hex_value in allowed_space:
            output.append(char)
        elif (colors and hex_value == 0x1b and i + 1 < len(untrusted_text) and
              untrusted_text[i + 1] == "[" and
              (sgr_match := re.match(sgr_pattern, untrusted_text[i + 2:]))):
            sgr_match_length = sgr_match.end()
            output.append(untrusted_text[i:i + 2 + sgr_match_length])
            i += sgr_match_length + 1
        else:
            output.append("_")
        i += 1

    return "".join(output)


def main() -> None:
    """Read untrusted text and sanitize it to be safely printed on the terminal.

    Examples
    --------
    From the shell, strings must be provided with escapes already interpreted:
    $ safe_print.py "$(printf '%b' "untrusted_string\033[2K")"
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("untrusted_text", nargs=argparse.REMAINDER,
                        help="text to print safely")
    args = parser.parse_args()
    untrusted_text = "\n".join(args.untrusted_text)
    print(safe_print(untrusted_text))


if __name__ == "__main__":
    main()
