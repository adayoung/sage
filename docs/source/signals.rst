.. _signals:

Signals
=======

Sage includes a "signal dispatcher" which helps allow decoupled applications
get notified when actions occur elsewhere in the framework. In a nutshell,
signals allow certain *senders* to notify a set of *receivers* that some action
has taken place. They're especially useful when many pieces of code may be
interested in the same events.

Sage provides a :doc:`set of built-in signals </ref/signals>` that let user
code get notified by Sage itself of certain actions.
You can also `define and send your own custom signals`_; see below.

.. _define and send your own custom signals: `defining and sending signals`_

Listening to signals
--------------------

To receive a signal, you need to register a *receiver* function that gets
called when the signal is sent by using the :meth:`Signal.connect` method:

.. method:: Signal.connect(receiver, [sender=None, weak=True, dispatch_uid=None])

    :param receiver: The callback function which will be connected to this
        signal. See :ref:`receiver-functions` for more information.

    :param sender: Specifies a particular sender to receive signals from. See
        :ref:`connecting-to-specific-signals` for more information.

    :param weak: Sage stores signal handlers as weak references by
        default. Thus, if your receiver is a local function, it may be
        garbage collected. To prevent this, pass ``weak=False`` when you call
        the signal's ``connect()`` method.

    :param dispatch_uid: A unique identifier for a signal receiver in cases
        where duplicate signals may be sent. See
        :ref:`preventing-duplicate-signals` for more information.

Let's see how this works by registering a signal that
gets called every time we successfully log into Achaea. We'll be connecting to the
:data:`~sage.signals.player_connected` signal.

.. _receiver-functions:

Receiver functions
~~~~~~~~~~~~~~~~~~

First, we need to define a receiver function. A receiver can be any Python
function or method:

.. code-block:: python

    def my_callback(signal, **kwargs):
        print("Request finished!")

Notice that the function takes a ``signal`` argument, along with wildcard
keyword arguments (``**kwargs``); all signal handlers must take these arguments.

We'll look at senders a bit later, but right now look at the ``**kwargs``
argument. All signals send keyword arguments, and may change those keyword
arguments at any time. In the case of
:data:`~sage.signals.player_connected`, it's documented as sending no
arguments, which means we might be tempted to write our signal handling as
``my_callback(signal)``.

This would be wrong -- in fact, Sage might throw an error if you do so. That's
because at any point arguments could get added to the signal and your receiver
must be able to handle those new arguments.

.. _connecting-receiver-functions:

Connecting receiver functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To connect a receiver to a signal, you use that signal's ``connect`` method:

.. code-block:: python

    from sage.signals import player_connected

    player_connected.connect(my_callback)

Now, our ``my_callback`` function will be called each time a request finishes.

.. _preventing-duplicate-signals:

Preventing duplicate signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some circumstances, the code connecting receivers to signals may run
multiple times. This can cause your receiver function to be registered more
than once, and thus called multiples times for a single signal event.

If this behavior is problematic (such as when using signals to
send an email whenever a model is saved), pass a unique identifier as
the ``dispatch_uid`` argument to identify your receiver function. This
identifier will usually be a string, although any hashable object will
suffice. The end result is that your receiver function will only be
bound to the signal once for each unique ``dispatch_uid`` value.

.. code-block:: python

    from sage.signals import player_connected

    player_connected.connect(my_callback, dispatch_uid="my_unique_identifier")

Defining and sending signals
----------------------------

Your applications can take advantage of the signal infrastructure and provide
its own signals.

Defining signals
~~~~~~~~~~~~~~~~

.. class:: Signal([providing_args=list])

All signals are :class:`sage.dispatch.signal.Signal` instances. The
``providing_args`` is a list of the names of arguments the signal will provide
to listeners. This is purely documentational, however, as there is nothing that
checks that the signal actually provides these arguments to its listeners.

For example:

.. code-block:: python

    from sage.dispatch.signal import Signal

    pizza_done = Signal(providing_args=["toppings", "size"])

This declares a ``pizza_done`` signal that will provide receivers with
``toppings`` and ``size`` arguments.

Remember that you're allowed to change this list of arguments at any time, so getting the API right on the first try isn't necessary.

Sending signals
~~~~~~~~~~~~~~~

To send a signal, call either :meth:`Signal.send`.
You must provide the ``sender`` argument, and may provide as many other keyword
arguments as you like.

.. method:: Signal.send(**kwargs)

For example, here's how sending our ``pizza_done`` signal might look:

.. code-block:: python

    class PizzaStore(object):
        ...

        def send_pizza(self, toppings, size):
            pizza_done.send(toppings=toppings, size=size)
            ...

``send()`` returns a list of tuple pairs
``[(receiver, response), ... ]``, representing the list of called receiver
functions and their response values.

``send()`` catches all errors derived from Python's ``Exception`` class,
and ensures all receivers are notified of the signal. If an error occurs, the
error instance is returned in the tuple pair for the receiver that raised the error.

Disconnecting signals
---------------------

.. method:: Signal.disconnect([receiver=None, sender=None, weak=True, dispatch_uid=None])

To disconnect a receiver from a signal, call :meth:`Signal.disconnect`. The
arguments are as described in :meth:`.Signal.connect`.

The *receiver* argument indicates the registered receiver to disconnect. It may
be ``None`` if ``dispatch_uid`` is used to identify the receiver.

Credit
~~~~~~

Sage's signals are heavily inspired by Django's signals (as is this documentation). Full credit
to the Django project.