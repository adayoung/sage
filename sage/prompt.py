# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage.player as player
from sage.signals import prompt_stats


class PromptRenderer(object):

    def __init__(self):
        self.stats = None
        self.raw = None

    def receive(self, raw, stats):
        self.raw = raw
        self.stats = stats

    def render(self):
        return self.raw


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

    stats = prompt.split(' ')[-1][:-1]

    if 'x' in stats:
        player.balance.on()
    else:
        player.balance.off()

    if 'e' in stats:
        player.equilibrium.on()
    else:
        player.equilibrium.off()

    prompt_stats.send(sender=renderer, stats=stats)

    renderer.receive(raw, stats)

    return renderer.render()


#: :py:class:`PromptRenderer` instance for building prompts
renderer = PromptRenderer()
