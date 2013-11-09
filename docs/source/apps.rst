.. apps:

Apps
====

Everything you write using Sage is considered an "app". They can be quite simple
such as a sipper or a highlighter or incredibly complex such as a curing
system. Perhaps the most powerful feature is multiple apps can be combined
together.

Structure of a Sage Application
-------------------------------

Sage applications are typically structured as follows: ::

    /my_application
      ├── __init__.py
      ├── /apps
      ├── /aliases
      ├── /triggers
      ├── meta.py
      ├── my_application.py

**Parent directory (/my_application)**

Put your app in a directory with the same name as your entry-point file.

**__init__.py**

This makes your app a Python Package.

**/apps**

This directory will contain other apps that your app requires.

**/aliases**

Your SML and Python files for aliases could go here.

**/triggers**

Your SML and Python files for triggers could go here.

**meta.py**

Contains extra (meta) information and settings for your app.

**Entry point (my_application.py)**

This is the starting point for your app. It must be the same name as the
directory of your app.

meta.py
-------

`meta.py` contains information about your app.

Installed Apps
~~~~~~~~~~~~~~

Sage apps can include other applications. This is great for collaboration with
other developers or separating responsibilities in your apps. To include other
apps they need to either be in your `apps` directory or available on your
`PYTHONPATH` (like an installed Python package).

To include other apps you must have a tuple in `meta.py` called
`installed_apps`. Sage will load the apps it can find with those names.
Here's an example: ::

    installed_apps = (
        'awesome_curing',
        'name_highlighter',
        'sailing',
        'bass_pro_fisher',
        'best_who_ever'
    )

Other Attributes
~~~~~~~~~~~~~~~~

**name**

A more descriptive name for the app.

**description**

A short description of what the app does.

**version**

A tuple representing the app's version. Example: ::

    version = (1, 0, 2)  # Major version 1, release 2 (1.0.2)

Meta Example
````````````

::

  name = "Sarapis' Curing System"
  description = "The curing of the Logos"
  version = (3, 1, 9)
  installed_apps = (
    'black_boar_autohug',
    'randomzap'
  )

Entry Point
-----------

The entry point for your app (a python file with the same name as your app)
has an optional interface with four basic methods: `init`, `unload`, `pre_reload`,
and `post_reload`. A basic entry point could look like the following: ::

    def init():
      """ This method will be called when the app is loaded (after it is
      imported). Any apps in meta.py's `installed_apps` will have already been
      loaded before this is called. """


    def unload():
      """ Called when an app is unloaded (or reloaded). """


    def pre_reload():
      """ Called before the app is reloaded. """


    def post_reload():
      """ Called after the app is reloaded. """

sage.apps
---------

If you wanted to access another loaded app, you can address it through
:py:mod:`sage.apps`. For example, if there was an app called "demo", you could
access it in another app with `sage.apps.demo` as if you were referencing the
module itself.

You can also just import the app package directly if it has already been loaded. ::

  from awesome_curing import awesome_curing  # the entry point file awesome_curing.py

  awesome_curing.affliction('anorexia')

Consider reading up on Python `packages <http://stackoverflow.com/questions/7948494/whats-the-difference-between-a-python-module-and-a-python-package>`_ if this confuses you.

Auto-Reloading
--------------

Sage monitors your app's files and reloads them when a change is detected.
Any errors will be displayed in the console.

.. warning::

    Auto-reloading is a new and fairly untested feature. Reloading live code
    in Python is unfortunately a difficult task. It's likely some aspects of
    your app will not reload as gracefully as intended. Please report whatever
    issues you have so they can be addressed and this feature improved.
