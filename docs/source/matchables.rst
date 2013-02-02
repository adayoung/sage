.. _matchables:

Matchables
==========

Sage comes with its own built-in triggers and aliases known collectively as
'Matchables'. Some features of Sage Matchables include:

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



.. _matchables-ownership:

Ownership
---------

Coming soon...