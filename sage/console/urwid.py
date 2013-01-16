#!/usr/bin/env python
from __future__ import absolute_import
import urwid
from sage.telnet import reactor
from sage.signals import telnet as telnet_signals
from sage.signals import gmcp as gmcp_signals

banner = """
The SAGE Framework v2.0.0
http://github.com/astralinae/sage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ready to connect

-
"""


class ReverseWalker(urwid.SimpleFocusListWalker):

    def write(self, line):
        self.append(line)
        self.set_focus(len(self) - 1)


class Header(object):

    def __init__(self):
        self.window_txt = urwid.Text('[Window: Log]', align='left')
        self.status_txt = urwid.Text('Status: Disconnected', align='center')
        self.ping_txt = urwid.Text('Ping: N/A', align='center')
        self.title_txt = urwid.Text(u'SAGE 2.0.0', align='right')

        self.cols = urwid.Columns([
            self.window_txt,
            self.status_txt,
            self.ping_txt,
            self.title_txt
        ])

    def get(self):
        return self.cols


class SageConsoleUI(object):

    palette = [
        ('header', 'white', 'dark green'),
        ('body', 'default', 'default'),
        ('footer', 'white', 'dark blue'),
    ]

    def __init__(self):

        self.log_list = list()

        # setup banner
        for line in banner.split('\n'):
            self.log_list.append(urwid.Text(line))

        self.log_walker = ReverseWalker(self.log_list)
        self.log = urwid.ListBox(self.log_walker)

        self.body = self.log

        self.header = Header()
        self.header_cols = urwid.AttrWrap(self.header.get(), 'header')
        self.frame = urwid.Frame(self.body, header=self.header_cols)

        twisted_loop = urwid.TwistedEventLoop(
            reactor=reactor,
            manage_reactor=True  # this isn't how I want to do it...
        )

        self.loop = urwid.MainLoop(self.frame, self.palette,
            unhandled_input=self.handle_keys, event_loop=twisted_loop)

        telnet_signals.connected.connect(self.connect)
        telnet_signals.disconnected.connect(self.disconnect)
        gmcp_signals.ping.connect(self.ping)

    def handle_keys(self, key):
        if key == 'f1':
            self.view = self.log
            self.writelog('f1')
            self.frame._invalidate()
        elif key == 'f2':
            self.writelog('f2')
            self.frame._invalidate()

    def writelog(self, msg):
        self.log_walker.write(urwid.Text(msg))

    def run(self):

        self.loop.run()

    def ping(self, sender, **kwargs):
        value = kwargs['latency']

        # convert to readable ms
        value = int(round(value * 1000))
        self.view.header.ping_txt.set_text('Ping: %sms' % value)
        self.loop.draw_screen()

    def connect(self, sender, **kwargs):
        self.view.header.status_txt.set_text('Status: Connected')
        self.loop.draw_screen()

    def disconnect(self, sender, **kwargs):
        self.view.header.status_txt.set_text('Status: Disconnected')
        self.view.header.ping_txt.set_text('Ping: N/A')
        self.loop.draw_screen()


app = SageConsoleUI()
