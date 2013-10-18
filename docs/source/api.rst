.. _api:

API
===

.. module:: sage

This part of the documentation covers all the interfaces of Sage.  For
parts where Sage depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

`sage`
------

Main Methods
~~~~~~~~~~~~

The following are some primary methods available from the `sage` namespace.

.. autofunction:: echo
.. autofunction:: send
.. autofunction:: defer_to_prompt

Main States
~~~~~~~~~~~
.. autodata:: connected

Main Containers
~~~~~~~~~~~~~~~
.. autodata:: config
.. autodata:: apps
.. autoclass:: sage.app.Apps
    :members:
.. autodata:: buffer
.. autoclass:: sage.inbound.Buffer
    :members:
.. autodata:: aliases
.. autodata:: triggers

`sage.ansi`
-----------

.. automodule:: sage.ansi
  :members:
.. autofunction:: sage.ansi.white
.. autofunction:: sage.ansi.black
.. autofunction:: sage.ansi.red
.. autofunction:: sage.ansi.green
.. autofunction:: sage.ansi.yellow
.. autofunction:: sage.ansi.blue
.. autofunction:: sage.ansi.magenta
.. autofunction:: sage.ansi.cyan
.. autofunction:: sage.ansi.grey
.. autofunction:: sage.ansi.bold_white
.. autofunction:: sage.ansi.bold_red
.. autofunction:: sage.ansi.bold_green
.. autofunction:: sage.ansi.bold_yellow
.. autofunction:: sage.ansi.bold_blue
.. autofunction:: sage.ansi.bold_magenta
.. autofunction:: sage.ansi.bold_cyan

`sage.inbound`
--------------
.. automodule:: sage.inbound
    :members:

`sage.matching`
---------------
.. automodule:: sage.matching
    :members:

`sage.player`
-------------
.. automodule:: sage.player
    :members:

`sage.sml`
-------------
.. automodule:: sage.sml
    :members: