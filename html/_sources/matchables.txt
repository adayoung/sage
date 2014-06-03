.. _matchables:

Matchables
==========

Sage comes with its own built-in triggers and aliases known collectively as
'matchables'. Some features of Sage Matchables include:

* Optimized for high performance.
* Supports group hierarchies.
* Different types of matching (string methods, regex, etc).
* Bind Python methods to successful matches.
* An organized API for interacting with matchables and groups.
* A powerful alternative syntax for writing large numbers of matchables.

Matchables are divided into two primary 'master groups':
:py:obj:`~sage.triggers` and :py:obj:`~sage.aliases`. Triggers run on
the lines coming in from Achaea. Aliases run on the input you enter into your
client.

Matchable Types
---------------

There are different types of matching allowing you to pick the best tool for
the job. *A 'line' in this reference means a line received from either the
server or the client.*

========== ================================================================================
Type       Description
========== ================================================================================
regex      'Regular Expression'. Powerful matching capability through Python's `re` module.
exact      Exact string matching. :samp:`s == line`
substring  A string that is part of a line. :samp:`s in line`
startswith A string that is the beginning of a line. :samp:`line.startswith(s)`
endswith   A string that is the end of a line. :samp:`line.endswith(s)`
========== ================================================================================

Creating Matchables
-------------------

Groups
``````

All matchables belong to a group, and whenever you create one it will be
relative to whatever group you want it to belong to. Therefor, you'll need to
create groups first. Sage supports full hierarchies of groups: ::

    from sage import aliases  # `aliases` is the master group

    group_1 = aliases.create_group('group_1', app='thisapp')

    group_2 = group_1.create_group('group_2')

    # top-level groups must be owned by an app
    group_3 = aliases.create_group('group_3', app='thisapp')

    group_4 = group_2.create_group('group_4', enabled=False)

Will create the following structure: ::

    +-group_1
    |  +-group_2
    |    +-group_4  (this group is disabled)
    +-group_3

.. note::

    While Sage has parent-child relationships between groups, there is no
    actual order of execution with matchables. Matchables belonging to a
    parent group are not guaranteed to execute before a child group's
    matchables. While this might seem like a loss if you're used to writing for
    other clients, experience has proven depending on order-of-execution
    is a poor design. With Sage, worrying the order of your matchables is
    unnecessary. Use groups to keep your code organized - not to actually
    create the logic of your application.

.. _matchables-ownership:

Group Ownership
~~~~~~~~~~~~~~~

Sage requires any top-level group to be assigned to an app. This is necessary
for reloading and unloading of apps. Any child group will assume ownership of
its parent, but can be overridden during group creation. Ownership is declared
by passing the string name of an app as the ``app`` parameter to
:py:meth:`~sage.matching.Group.create_group`


Creating and Binding
````````````````````

When you write a matchable, you will want to bind methods to it that will be
called if there is a successful match. Sage has multiple ways of creating
matchables and binding methods to them.

With `<group>.create()`
~~~~~~~~~~~~~~~~~~~~~~~

Matchables can be created from a group with
:py:meth:`~sage.matching.Group.create`. Please see the
:py:meth:`API <sage.matching.Group.create>` to see all the parameters.
Example: ::

    # This will be run if the 'eq_recovered' trigger matches
    def eq_recovered(trigger):
        pass  # do stuff when equilibrium is recovered

    group.create(
        "eq_recovered",  # name of the matchable
        "exact",  # type of matchable
        "You have recovered equilibrium.",  # pattern
        [eq_recovered]  # list of methods bound to matchable
    )

Here's an example of a matchable with a parameter: ::

    # The 'affliction' trigger method will receive a parameter
    def affliction(trigger, affliction):
        player.afflictions.add(affliction)

    group.create(
        "paralysis",  # name of the matchable
        "exact",  # type of matchable
        "You feel your limbs stiffen and lock up in response to an unseen power.",  # pattern
        [affliction, "paralysis"]  # method and parameter to be passed
    )

With a decorator
~~~~~~~~~~~~~~~~

Using a
`decorator <http://docs.python.org/2/reference/compound_stmts.html#function>`_
is a convenient way to create a matchable and bind it to a method at the same
time. ::

    @group.exact("You have recovered equilibrium.")
    def eq_recovered(trigger):
        pass  # do stuff when equilibrium is recovered

The decorator mimics the parameters of :py:meth:`~sage.matching.Group.create`.
In absence of ``name`` being passed in the decorator, the matchable will have
the same name as the method bound to it.


Binding Methods to Existing Matchables
``````````````````````````````````````

You can bind a method to an existing matchable by using the matchable's
:py:meth:`~sage.matching.Matchable.bind` method. Similarly, you can
:py:meth:`~sage.matching.Matchable.unbind` as well. Matchables can have
multiple methods bound to them.

Parameters
``````````

An optional single parameter can be passed to each matchable method when you
bind them. This is helpful if you are using one method for many matchables.

Delaying
````````

Sometimes you'll not want to take action at the immediate time a line is
matched. For this, Sage allows you to delay a matchable running its bound
methods. ::

    @group.exact("Something horrible will happen in 5 seconds.", delay=5)
    def delay_example(trigger):
        pass  # this will run 5 seconds after being matched


Bound Methods
-------------

Every method bound to a matchable will be passed a single parameter: the
instance of the matchable. This object will have different attributes and
behaviors depending on which matchable type it is.

**all matchables** ::

    # Line: "Sage has many ways to match a line."
    @group.exact('Sage has many ways to match a line.')
    def example(trigger):

        trigger.line  # "Sage has many ways to match a line."

        trigger.time  # time the match occurred (seconds since Epoch)

        # enable/disable the matchable
        trigger.disable()
        trigger.enable()

        # matchable's group or 'parent'
        trigger.parent()

        # delete the matchable
        trigger.destroy()

        # example of how you might disable the matchable's group
        trigger.parent().disable()


**regex** ::

    # Line: "Sage has many ways to match a line."
    @group.regex('^Sage has (many|few) ways')
    def example(trigger):

        # regex groups
        trigger.groups  # ('many')

        # The re.MatchObject returned from matching the pattern
        # See: http://docs.python.org/2/library/re.html#re.MatchObject
        trigger.matchobj

**exact** ::

    no extra attributes

**substring** ::

    # Line: "Sage has many ways to match a line."
    @group.substring('has many ways')
    def example(trigger):

        # prefix, what came before the pattern in the line
        trigger.prefix  # 'Sage '

        # suffix, what came after the pattern
        trigger.suffix  # ' to match a line.'

**startswith** ::

    # Line: "Sage has many ways to match a line."
    @group.startswith('Sage has many')
    def example(trigger):

        # suffix, what came after the pattern
        trigger.suffix  # ' ways to match a line.'

**endswith** ::

    # Line: "Sage has many ways to match a line."
    @group.endswith('match a line.')
    def example(trigger):

        # prefix, what came before the pattern in the line
        trigger.prefix  # 'Sage has many ways to '

Selecting Matchables
--------------------

You can get the instance of a matchable by calling
:py:meth:`~sage.matching.Group.get` on its group with the name of the
matchable: ::

    # find a matchable called 'my_alias' in the group assigned to my_aliases
    my_alias = my_aliases.get('my_alias')

You can shortcut this by just calling the group itself: ::

    # shortcut to .get()
    my_alias = my_aliases('my_alias')

You can 'walk' through groups to a matchable by using '/' to define the
structure. Assume the following structure: ::

    +-group_1
      +-group_2
        +-group_3
          +-my_trigger

The following call to get would return `my_trigger`: ::

    my_trigger = group_1('group_2/group_3/my_trigger')

If :py:meth:`~sage.matching.Group.get` can't find a matchable it will then
attempt to find a group with the name you provided: ::

    group_3 = group_1('group_2/group_3')

If you're specifically looking for a group you can also use
:py:meth:`~sage.matching.Group.get_group`: ::

    group_3 = group_1.get_group('group_2/group_3')

You can do method chaining with :py:meth:`~sage.matching.Group.get`: ::

    # disables my_trigger
    group_1('group_2/group_3/my_trigger').disable()

In this final example we'll enable a matchable in another group from a bound
method. Assume the following structure: ::

    +-app
       +-group_1
       |  +-trigger_1
       +-group_2
          +-trigger_2 (disabled)

When `trigger_1` gets matched, it will enable trigger_2: ::

    @group_1.exact("Something is coming!")
    def trigger_1(trigger):
        trigger.parent().parent().get('group_2/trigger_2').enable()
