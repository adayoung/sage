.. _quickstart:

Quickstart
==========

Ready to get started?  This page gives a good introduction to Sage.  It
assumes you already have Sage installed.  If you do not, head over to the
:ref:`installation` section. Lets go!

A Truly 'Minimal' Application
-----------------------------

Lets make your first Sage app. Create a file called `myapp.py`:

.. code-block:: console

    $ touch myapp.py

Now run it with Sage:

.. code-block:: console

    $ sage myapp.py

Sage is now running your app and gives you some port numbers for the proxy and
the 'backdoor' (which we'll cover later). You can now connect your MUD client
to `127.0.0.1:5493`. Congratulations, you have made your first app without
writing a single line of code!

.. note::

    You can stop Sage by doing `Ctrl+C` (also known as `SIGINT <http://en.wikipedia.org/wiki/SIGINT_(POSIX)#SIGINT>`_)

Cool as that is, it's not terribly useful. Now lets make a trigger for the
'exits' line you'd see in every room in Achaea. In `myapp.py`: ::

    from sage import echo, triggers

    @triggers.trigger(pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$", type="regex")
    def exits(trigger):
        echo('Exits detected!')

You've created a regular expression or `regex` trigger. If you're not familiar
with `regular expressions <http://xkcd.com/208/>`_, you should research them as
they are vital to making apps with Sage. Now whenever you see an exit, you'll
see a line where Sage is echoing "Exits detected!" to you.







