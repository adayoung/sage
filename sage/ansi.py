# -*- coding: utf-8 -*-
"""
sage.ansi
~~~~~~~~~

Helper methods for ANSI formatting and colors.

This is hardly compliant to the standard. Please don't use this for anything
but Achaea.

A sage color tuple works in this format:
    (bright/bold, foreground, background, underline)

We don't support other (less-supported) options like blink, etc.
"""

import re

# for finding ANSI color sequences
ANSI_COLOR_REGEXP = re.compile('(' + chr(27) + '\[[0-9;]*m)')


def filter(text):
    """ Takes in text and filters out the ANSI color codes. """

    return ANSI_COLOR_REGEXP.sub('', text)


def split(text):
    """ Splits text and ANSI color sequences """

    return ANSI_COLOR_REGEXP.split(text)


def split_expanded(text):
    """ Split a string into string parts and tuples of color sequences """

    processed = list()
    parts = split(text)

    for part in parts:
        if len(part) == 0:
            continue

        if part[0] != chr(27):
            processed.append(part)
            continue

        # we make the ridiculous assumption anything not defined as X;X is 0;X
        if ';' not in part:
            code = '0;' + part[2:-1]
        else:
            code = part[2:-1]

        processed.append(code)

    return processed
