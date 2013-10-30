# -*- coding: utf-8 -*-
import sage


def receiver(line):

    sage.aliases.in_loop = True

    out = line

    # run trigger matching over lines
    for alias in sage.aliases.enabled:

        # if we match, don't return the line. Expect the method to send for us.
        if alias.match(line):
            if alias.intercept is True:
                out = None

    sage.aliases.flush_set()
    sage.aliases.in_loop = False

    return out
