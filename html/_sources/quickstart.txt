.. _quickstart:

Quickstart
==========

Ready to get started?  This page gives a good introduction to Sage.  It
assumes you already have Sage installed.  If you do not, head over to the
:ref:`installation` section. Lets go!

A Minimal Application
-----------------------------

Lets make your first Sage app. Create a file called `myapp.py`:

.. code-block:: console

    $ touch myapp.py

Now run it with Sage:

.. code-block:: console

    $ sage myapp.py

Sage is now running your app and gives you some port numbers for the proxy and
the ':ref:`backdoor`' (which we'll cover later). You can now connect your MUD client
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

Lets go over the parts of this snippet. We import two objects from
:py:mod:`sage`: :py:meth:`~sage.echo` and :py:data:`~sage.triggers`. The latter
is technically the top-level :py:class:`group <sage.matching.Group>` of
triggers in Sage. From that group, we use a
`decorator <http://docs.python.org/2/reference/compound_stmts.html#function>`_
(declared by the @) to call the :py:meth:`~sage.matching.TriggerGroup.trigger`
method and pass it two parameters. The ``pattern`` is what we match against and
the ``type`` is the type of trigger it is (in this case 'regex'). We 'wrap'
:py:meth:`exits` with the decorator to :py:data:`~sage.matching.Matchable.bind`
it to the trigger it creates for you.

In Sage, triggers and aliases are better known as `matchables` since they are
identical. Methods bound to matchables like :py:meth:`exits` accept a single
parameter that is the :py:class:`~sage.matching.Matchable` instance they
belong to.

Taking It To The Next Level
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lets use our new exits trigger to make the exits more readable. Assume the line
we are processing is: ::

    You see exits leading north, east, south, west, up (open door), down, and out.

First, we need to break up the exits into a
`list <http://docs.python.org/2/tutorial/introduction.html#lists>`_: ::

    @triggers.trigger(pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$", type="regex")
    def exits(trigger):

        # get the second regex group (0 would be the first)
        exit_str = trigger.groups[1]

        # exit_str now is "north, east, south, west, up (open door), down, and out"

        # lets remove 'and' from the string for sake of consistency
        exit_str = exit_str.replace(' and', '')

        # exit_str now is "north, east, south, west, up (open door), down, out"

        # now break up the exits into a list and trim off any white space
        # To do this, we'll use a list comprehension
        exits = [e.strip() for e in exit_str.split(',')]

        # exits now is ['north', 'east', 'south', 'west', 'up (open door)', 'down', 'out']

Notice that the `trigger` object already had the regular expression groups for
you.

