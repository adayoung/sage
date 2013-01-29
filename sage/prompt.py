# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage.player as player


def receiver(raw):
    """ Receives the raw prompt text and parses """

    # strip out the colors
    prompt = ansi.filter_ansi(raw)

    # What is this??
    if '-' not in prompt:
        return raw

    if prompt[0] == '-':
        # we're in blackout...
        pass

    stats = prompt.split(' ')[-1]

    if 'x' in stats:
        player.balance.on()
    else:
        player.balance.off()

    if 'e' in stats:
        player.equilibrium.on()
    else:
        player.equilibrium.off()

    """
    TODO!
    c - cloak
    b - blind
    d - deaf
    k - kola
    """

    return raw
