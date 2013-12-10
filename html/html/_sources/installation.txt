.. _installation:

Installation
============

.. warning::
    Sage is currently alpha-stage software. The API will be changing often.
    Please take this into consideration before you begin any significant
    development with Sage.

Sage works with CPython version 2.7 and greater, but it will not work (yet) with
Python 3 as `Twisted <http://twistedmatrix.com>`_ (a dependency) hasn't fully
supported it yet. Sage also can be used with `PyPy <http://pypy.org/>`_.

It's also recommended to have `libyaml <http://pyyaml.org/wiki/LibYAML>`_
installed but not required.

.. warning::
    Sage currently does not support Windows. Please read :ref:`windows`
    for more info.

Using Pip
---------

Pip makes installing Sage and its dependencies painless.

.. code-block:: console

    $ pip install -e git+https://github.com/spicerack/sage.git#egg=sage

Manually
--------

Because of `Issue #4 <https://github.com/spicerack/sage/issues/4>`_, you might
have to install `pyasn1` manually first if you are using a virtualenv:

.. code-block:: console

    $ pip install pyasn1

Clone Sage and build with `setup.py`:

.. code-block:: console

    $ git clone git://github.com/spicerack/sage.git
    $ cd sage
    $ python setup.py install

Screenwidth 0
-------------

The only configuration option Sage requires in Achaea is `screenwidth 0`. Sage
is not (nor ever will be) designed to work with screenwidth 80.

.. code-block:: console

    config screenwidth 0
