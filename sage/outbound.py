# -*- coding: utf-8 -*-
import sage


def receiver(line):

    # run trigger matching over lines
    for alias in sage.aliases.enabled:

        # if we match, don't return the line. Expect the method to write for us.
        if alias.match(line):
            return None

    return line
