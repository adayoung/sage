# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
from twisted.internet import reactor, defer, threads
from twisted.python import threadable
threadable.init()
from code import InteractiveConsole as _InteractiveConsole
try:
    import readline  # gives us command history in the console
    # gives us tab-completion, yay!
    import rlcompleter
    readline.parse_and_bind("tab:complete")
except ImportError:
    print("ImportError: readline not available")
    pass


class TwistedInteractiveConsole(_InteractiveConsole):
    """Closely emulate the behavior of the interactive Python interpreter,
    but run from within Twisted's reactor!
    """

    def __init__(self, locals=None, filename="<console>"):
        _InteractiveConsole.__init__(self, locals, filename)

    def interact(self, banner=None, stopReactor=False):
        """
        The optional banner argument specify the banner to print
        before the first interaction

        The optional stopReactor argument indicates whether to stop
        the Twisted reactor when the user exits the interpreter (^Z).

        """
        self.stopReactor = stopReactor
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

        if banner is None:
            banner_info = (
                sys.version_info[0],
                sys.version_info[1],
                sys.version_info[2],
                sys.platform
            )
            self.write("SAGE Interactive Console using Python %s.%s.%s on %s (Ctrl+D to force quit)\n" % (banner_info))
        else:
            self.write("%s\n" % str(banner))

        reactor.callLater(0, self._startInteraction)

    def _startInteraction(self, more=False):
        if more:
            prompt = sys.ps2
        else:
            prompt = sys.ps1
        d = defer.maybeDeferred(self.raw_input, prompt)
        d.addCallbacks(self._processInput, self._processInputError)

    def _processInput(self, line):
        #Twisted will raise an exception if you exit inside a defered
        strip_line = line.strip()
        if strip_line == 'exit()' or strip_line == 'sys.exit()' or strip_line == 'quit()':
            reactor.callWhenRunning(reactor.stop)
            return
        more = self.push(line)
        reactor.callLater(0, self._startInteraction, more)

    def _processInputError(self, failure):
        failure.trap(EOFError)
        self.write("\n")
        if bool(self.stopReactor):
            reactor.stop()

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        raw_input(); a subclass may replace this with a different
        implementation.

        """
        return threads.deferToThread(raw_input, prompt)


def interact(banner=None, readfunc=None, local=None, stopReactor=False):
    """Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- if not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()
    stopReactor -- passed to InteractiveConsole.interact()

    """
    console = TwistedInteractiveConsole(local)
    if readfunc is not None:
        console.raw_input = readfunc

    console.interact(banner, stopReactor)
