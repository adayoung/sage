# -*- coding: utf-8 -*-
"""
sage.ansi
~~~~~~~~~

Helper methods for ANSI formatting and colors
"""

import re

# for finding ANSI color sequences
ANSI_COLOR_REGEXP = re.compile(chr(27) + '\[[0-9;]*[m]')


def filter(text):
    """ Takes in text and filters out the ANSI color codes. """

    return ANSI_COLOR_REGEXP.sub('', text)
