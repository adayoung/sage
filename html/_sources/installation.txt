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

Using Pip
---------

Pip makes installing Sage and its dependencies painless.

.. code-block:: console

    pip install -e git+https://github.com/astralinae/sage.git#egg=sage

