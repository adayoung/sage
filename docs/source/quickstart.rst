.. _quickstart:

Quickstart
==========

Ready to get started?  This page gives a good introduction to Sage.  It
assumes you already have Sage installed.  If you do not, head over to the
:ref:`installation` section. Lets go!

A Minimal Application
-----------------------------

Lets make your first Sage app. Sage has a built-in utility to help get you
started by using `sage mkapp`:

.. code-block:: console

    $ sage mkapp -m quickstart

The `-m` flag tells Sage to make this a basic app.

Sage will ask you some basic questions like what the name of the app is,
its version, etc. Just accept the defaults for now (press enter).

Now run it with Sage:

.. code-block:: console

    $ sage run quickstart

Sage is now running your app and gives you some port numbers for the proxy and
the ':ref:`backdoor`' (which we'll cover later). You can now connect your MUD client
to `127.0.0.1:5493`. Congratulations, you have made your first app without
writing a single line of code!

.. note::

    You can stop Sage by doing `Ctrl+C` (also known as `SIGINT <http://en.wikipedia.org/wiki/SIGINT_(POSIX)#SIGINT>`_)

Cool as that is, it's not terribly useful. Now lets make a trigger for the
'exits' line you'd see in every room in Achaea. In `quickstart/quickstart.py`: ::

    from sage import echo, triggers

    @triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex")
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

    @triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex")
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
you. Now let's reformat this information in a better way with some color. Add
:py:mod:`~sage.ansi` to your imports: ::

    from sage import echo, triggers, ansi

Now modify that list comprehension to also color the exits: ::

    exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]

Now all of our exits will be in bright white. Lets turn the list back into a
string now: ::

    # joins the list as a string delimited by a comma and a space
    new_str = ', '.join(exits)

    # echo our new exits back to the client
    echo("Exits: " + new_str)

Not bad! Now we can see those exits much better, but this still isn't ideal.
The line we echo comes at the top of every room and the original exits line is
still there. While :py:meth:`~sage.echo` is easy to use, it's not the right
tool for this job. Instead, lets replace the actual exits line from the game.
Fortunately, Sage makes this very easy. Remove the call to
:py:meth:`~sage.echo` and replace it with: ::

    # replace the line's output with new_str
    trigger.line.output = "Exits: " + new_str

Sage provides you the matching line with `trigger.line`. This object is an
instance of the special :py:class:`sage.inbound.Line`.

.. warning::
    You must never use assignment (=) on a :py:class:`~sage.inbound.Line`! Only
    change its `.output` attribute.

Now we have nice easy to read exits. Here's the app in its entirety so far: ::

    from sage import triggers, ansi


    @triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex")
    def exits(trigger):
        # get the second regex group (0 would be the first)
        exit_str = trigger.groups[1]

        # lets remove 'and' from the string for sake of consistency
        exit_str = exit_str.replace('and', '')

        # now break up the exits into a list and trim off any white space while
        # adding color using a list comprehension
        exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]

        # joins the list as a string delimited by a comma and a space
        new_str = ', '.join(exits)

        # replace the line's output with new_str
        trigger.line.output = "Exits: " + new_str

Get Organized
~~~~~~~~~~~~~

It's not a good idea to just make triggers in the 'master' trigger group. Let's organize your trigger into its own :py:class:`~sage.matching.Group`. This is
how you'll actually handle your matchables in your apps.

.. note::
    You have to tell Sage which app 'owns' a group by passing the name of the
    the app in the ``app`` parameter for
    :py:meth:`~sage.matching.Group.create_group`. Failing to do this will
    raise :py:exc:`~sage.matching.OrphanedMatchableGroupError`. It's highly
    recommended you read more about :ref:`matchables-ownership`.

The code now changes to:

.. code-block:: python
    :emphasize-lines: 4,7

    from sage import triggers, ansi

    # create a new group called 'room' owned by the app 'quickstart'
    room_triggers = triggers.create_group('room', app='quickstart')

    # notice how the decorator changes to the group
    @room_triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex")
    def exits(trigger):
        exit_str = trigger.groups[1]
        exit_str = exit_str.replace('and', '')
        exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]
        new_str = ', '.join(exits)
        trigger.line.output = "Exits: " + new_str


Adding an Alias
~~~~~~~~~~~~~~~

Leaving our exits trigger enabled would be perfectly acceptable, but lets
say you only want it on when you 'ql' (quick-look in Achaea). To do this, you
need to make an alias. This works nearly identical to how triggers work:

.. code-block:: python
    :emphasize-lines: 1,6,10-13

    from sage import triggers, aliases, ansi, send  # notice we add send

    room_triggers = triggers.create_group('room', app='quickstart')

    # create a new aliases group (owned by 'quickstart')
    room_aliases = aliases.create_group('room', app='quickstart')


    # We create an alias similar to how we create a trigger
    @room_aliases.alias(pattern="ql", type="exact")
    def ql(alias):
        # send to Achaea
        send('ql')


    @room_triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex")
    def exits(trigger):
        exit_str = trigger.groups[1]
        exit_str = exit_str.replace('and', '')
        exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]
        new_str = ', '.join(exits)
        trigger.line.output = "Exits: " + new_str

Now modify your alias to enable the exits trigger, and change the exits trigger
to be disabled by default:

.. code-block:: python
    :emphasize-lines: 11,20,29

    from sage import triggers, aliases, ansi, send

    room_triggers = triggers.create_group('room', app='quickstart')

    room_aliases = aliases.create_group('room', app='quickstart')

    @room_aliases.alias(pattern="ql", type="exact")
    def ql(alias):

        # enable the exits trigger
        room_triggers('exits').enable()

        # send to Achaea
        send('ql')


    @room_triggers.trigger(
        pattern="^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$",
        type="regex",
        enabled=False)  # notice this is now disabled
    def exits(trigger):
        exit_str = trigger.groups[1]
        exit_str = exit_str.replace('and', '')
        exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]
        new_str = ', '.join(exits)
        trigger.line.output = "Exits: " + new_str

        # now disable this trigger
        trigger.disable()

Congratulations! Now the alias will enable the `exits` trigger whenever you
send "ql", and `exits` will disable itself after it runs. This is just a tiny
example of the things you can make with Sage. Continue reading the user guide
and try writing your own apps!
