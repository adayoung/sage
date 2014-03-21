=======
Signals
=======

A list of all the signals that Sage sends.

.. seealso::

    See the documentation on the :doc:`signal dispatcher </signals>` for
    information regarding how to register for and receive signals.

Core Signals
------------

.. module:: sage.signals
   :synopsis: Signals sent by Sage's core

The :mod:`sage.signals` module defines a set of basic signals sent by Sage.

pre_start
~~~~~~~~~

.. attribute:: sage.signals.pre_start
   :module:

.. ^^^^^^^ this :module: hack keeps Sphinx from prepending the module.

This signal is sent before the Sage server starts up.

Arguments sent with this signal:

``signal``
    The signal instance that just fired.

pre_prompt
~~~~~~~~~~

.. attribute:: sage.signals.pre_prompt
   :module:

