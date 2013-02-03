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
:py:meth:`~sage.matching.Group.create`. Example: ::

    # This will be run if the 'eq_recovered' trigger matches
    def eq_recovered(trigger):
        pass  # do stuff when equilibrium is recovered

    group.create(
        "eq_recovered",  # name of the matchable
        "exact",  # type of matchable
        "You have recovered equilibrium.",  # pattern
        [eq_recovered]  # list of methods bound to matchable
    )

With a decorator
~~~~~~~~~~~~~~~~

Using a
`decorator <http://docs.python.org/2/reference/compound_stmts.html#function>`_
is a convenient way to create a matchable and bind it to a method at the same
time. ::

    @group.trigger(pattern="You have recovered equilibrium.", type="exact")
    def eq_recovered(trigger):
        pass  # do stuff when equilibrium is recovered

The decorator mimics the parameters of :py:meth:`~sage.matching.Group.create`.
In absence of ``name`` being passed in the decorator, the matchable will have
the same name as the method bound to it.
