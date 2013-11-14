"""
simplesipper
~~~~~~~~~~~~

This is a rudimentary health and mana sipper only intended to be an example.

"""
from __future__ import division
import sage
from sage import player, triggers
from sage.contrib import Balance
from sage.signals import post_prompt

# create a new balance called player.sip
player.sip = Balance()

# create an app-level trigger group
ss = triggers.create_group('simplesipper', app='simplesipper')


def sip(vial):
    """ Takes a sip of health or mana """

    # Don't try to sip if we are off sip balance
    if player.sip == False:
        return

    # turn on the sip group
    sip_group.enable()

    # set the balance to the wait-state
    player.sip.wait()

    # send the sip to the server
    sage.send('sip ' + vial)


def onprompt(sender, **kwargs):
    """ runs every prompt """

    # we haven't gotten vital data yet
    if player.connected is False:
        return

    if player.health.percentage > 85 and player.mana.percentage > 85:
        return

    # very simple algorithm to choose between health and mana, come up with
    # your own!
    diff = player.health.percentage / player.mana.percentage

    if diff <= 1.0:
        sip('health')
    else:
        sip('mana')

# connect to sage.signals.post_prompt
post_prompt.connect(onprompt)


""" --- Triggers --- """

# this group will hold sip messages
sip_group = ss.create_group('sips', enabled=False)


# Health sip or mana sip taken
@sip_group.exact(name='sip_mana', pattern='Your mind feels stronger and more alert.')
@sip_group.exact(name='sip_health', pattern='The elixir heals and soothes you.')
def sip_trigger(trigger):
    # set sip balance to off
    player.sip.off()

    # disable the 'sips' group
    trigger.parent().disable()

    # in 4 seconds, turn on the restored sip balance trigger
    sage.delay(4, lambda: ss('restored_balance').enable())


# Sip balance restored
@ss.exact('You may drink another health or mana elixir or tonic.', enabled=False)
def restored_balance(trigger):
    # set sip balance to on
    player.sip.on()

    # disable this trigger
    trigger.disable()
