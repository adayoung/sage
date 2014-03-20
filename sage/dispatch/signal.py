import sys
import threading
import weakref
from six.moves import xrange
from sage import _log

if sys.version_info < (3, 4):
    from .weakref_backports import WeakMethod
else:
    from weakref import WeakMethod


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


class Signal(object):

    def __init__(self, providing_args=None):

        self.receivers = []
        if providing_args is None:
            providing_args = []
        self.providing_args = set(providing_args)
        self.lock = threading.Lock()
        self._dead_receivers = False

    def connect(self, receiver, dispatch_uid=None):
        """
        Connect receiver to signal.

        Arguments:

            receiver
                A function or an instance method which is to receive signals.
                Receivers must be hashable objects.

                Receivers must be able to accept keyword arguments.

                If receivers have a dispatch_uid attribute, the receiver will
                not be added if another receiver already exists with that
                dispatch_uid.

            dispatch_uid
                An identifier used to uniquely identify a particular instance of
                a receiver. This will usually be a string, though it may be
                anything hashable.
        """

        if dispatch_uid:
            lookup_key = dispatch_uid
        else:
            lookup_key = _make_id(receiver)

        ref = weakref.ref
        receiver_object = receiver
        # Check for bound methods
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            ref = WeakMethod
            receiver_object = receiver.__self__
        if sys.version_info >= (3, 4):
            receiver = ref(receiver)
            weakref.finalize(receiver_object, self._remove_receiver)
        else:
            receiver = ref(receiver, self._remove_receiver)

        with self.lock:
            self._clear_dead_receivers()
            for r_key, _ in self.receivers:
                if r_key == lookup_key:
                    break
            else:
                self.receivers.append((lookup_key, receiver))

    def disconnect(self, receiver=None, dispatch_uid=None):
        """
        Disconnect receiver from signal.

        Arguments:

            receiver
                The registered receiver to disconnect. May be none if
                dispatch_uid is specified.

            dispatch_uid
                the unique identifier of the receiver to disconnect
        """
        if dispatch_uid:
            lookup_key = dispatch_uid
        else:
            lookup_key = _make_id(receiver)

        with self.lock:
            self._clear_dead_receivers()
            for index in xrange(len(self.receivers)):
                (r_key, _) = self.receivers[index]
                if r_key == lookup_key:
                    del self.receivers[index]
                    break

    def has_listeners(self):
        return bool(self._live_receivers())

    def _live_receivers(self):
        """
        Filter sequence of receivers to get resolved, live receivers.

        This checks for weak references and resolves them, then returning only
        live receivers.
        """
        receivers = None
        if receivers is None:
            with self.lock:
                self._clear_dead_receivers()
                receivers = []
                for receiverkey, receiver in self.receivers:
                    receivers.append(receiver)

        non_weak_receivers = []
        for receiver in receivers:
            if isinstance(receiver, weakref.ReferenceType):
                # Dereference the weak reference.
                receiver = receiver()
                if receiver is not None:
                    non_weak_receivers.append(receiver)
            else:
                non_weak_receivers.append(receiver)
        return non_weak_receivers

    def _clear_dead_receivers(self):
        # Note: caller is assumed to hold self.lock.
        if self._dead_receivers:
            self._dead_receivers = False
            new_receivers = []
            for r in self.receivers:
                if isinstance(r[1], weakref.ReferenceType) and r[1]() is None:
                    continue
                new_receivers.append(r)
            self.receivers = new_receivers

    def send(self, **named):
        """
        Send signal from signal to all connected receivers catching errors.

        Arguments:

            named
                Named arguments which will be passed to receivers. These
                arguments must be a subset of the argument names defined in
                providing_args.

        Return a list of tuple pairs [(receiver, response), ... ]. May raise
        DispatcherKeyError.

        If any receiver raises an error (specifically any subclass of
        Exception), the error instance is returned as the result for that
        receiver.
        """
        responses = []
        if not self.receivers:
            return responses

        # Call each receiver with whatever arguments it can accept.
        # Return a list of tuple pairs [(receiver, response), ... ].
        for receiver in self._live_receivers():
            try:
                response = receiver(signal=self, **named)
            except Exception as err:
                _log.err()
                responses.append((receiver, err))
            else:
                responses.append((receiver, response))
        return responses

    def _remove_receiver(self, receiver=None):
        # Mark that the self.receivers list has dead weakrefs. If so, we will
        # clean those up in connect, disconnect and _live_receivers while
        # holding self.lock. Note that doing the cleanup here isn't a good
        # idea, _remove_receiver() will be called as side effect of garbage
        # collection, and so the call can happen while we are already holding
        # self.lock.
        self._dead_receivers = True


class Hook(Signal):

    def send(self, sender, param=None):
        responses = []
        if not self.receivers:
            return responses

        # Call each receiver with whatever arguments it can accept.
        # Return a list of tuple pairs [(receiver, response), ... ].
        for receiver in self._live_receivers():
            try:
                if param:
                    response = receiver(sender, param)
                else:
                    response = receiver(sender)
            except Exception as err:
                _log.err()
                responses.append((receiver, err))
            else:
                responses.append((receiver, response))
        return responses


def receiver(signal, **kwargs):
    """
    A decorator for connecting receivers to signals. Used by passing in the
    signal (or list of signals) and keyword arguments to connect::

        @receiver(post_save)
        def signal_receiver(signal, **kwargs):
            ...

        @receiver([post_save, post_delete])
        def signals_receiver(signal, **kwargs):
            ...

    """
    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func
    return _decorator