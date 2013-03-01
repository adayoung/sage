.. apps:

Apps
====

Everything you write using Sage is considered an "app". They can be quite simple
such as a sipper or a highlighter or incredibly complex such as a curing
system. Perhaps the most powerful feature is multiple apps can be combined
together (called sub-apps).

Structure of a Sage Application
-------------------------------

While a Sage app can be a single Python file, typically you'll want to structure
your application as follows: ::

    /my_application
    ├── __init__.py
    ├── /apps
    ├── /aliases
    ├── /triggers
    ├── my_application.py

**Parent directory (/my_application)**

Put your app in a directory with the same name as your entry-point file.

**__init__.py**

This makes your app a Python Package. This will be useful to other apps that
might use yours.

**/apps**

This directory will contain sub-apps that your app requires.

**/aliases**

Your SML and Python files for aliases could go here.

**/triggers**

Your SML and Python files for triggers could go here.

**Entry point (my_application.py)**

This is the starting point for your app and is the file Sage imports when it is
loaded. It must be the same name as the directory of your app.

While this structure is recommended, it is not enforced. If it doesn't make
sense for your application then do what you think is best. *You* are the
developer!

Sub-Apps
--------

Sage apps can include other applications. This is great for collaboration with
other developers. To include other apps they need to either be in your `apps`
directory or available on your `PYTHONPATH` (like an installed Python package).

To include other apps you must have a tuple in your entry point called
`INSTALLED_APPS`. Here's an example: ::

    INSTALLED_APPS = (
        'awesome_curing',
        'name_highlighter',
        'sailing',
        'bass_pro_fisher',
        'best_who_ever'
    )

Sage will load the apps it can find with those names.

.. note::

    Having an app in `INSTALLED_APPS` doesn't import that app into the local
    namespace.