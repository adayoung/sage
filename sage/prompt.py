# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage.player as player
from sage.signals import prompt_stats
from sage.signals.player import blackout as blackout_signal
from sage import triggers

blackout_triggers = triggers.get_group('sage').create_group('blackout', enabled=False)

@blackout_triggers.exact('You have recovered equilibrium.')
def blackout_eq_on(trigger):
    player.equilibrium.on()


@blackout_triggers.exact('You have recovered balance on all limbs.')
def blackout_bal_on(trigger):
    player.balance.on()


class PromptRenderer(object):

    def __init__(self):
        self.stats = None
        self.raw = None

    def receive(self, raw, stats):
        self.raw = raw
        self.stats = stats

    def render(self):
        return self.raw

    def render_blackout(self):
        return ansi.grey('(blackout)-')


def receiver(raw):
    """ Receives the raw prompt text and parses """

    # strip out the colors
    prompt = ansi.filter_ansi(raw)

    # What is this??
    if '-' not in prompt:
        return raw

    if prompt[0] == '-':
        player.blackout = True
        blackout_signal.send(sender=None, blackout=True)
        blackout_triggers.enable()
        return renderer.render_blackout()

    if player.blackout is True:
        blackout_signal.send(sender=None, blackout=False)
        player.blackout = False
        blackout_triggers.disable()

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
