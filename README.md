*sage2 is under heavy initial development and won't be useful to anyone until I finish and write documentation. Stay tuned!

![Sage Logo](https://raw.github.com/astralinae/sage/master/docs/source/_static/logo-full.png)
Sage -- A Python Framework and Proxy for Achaea
===============================================

## Description

Sage is a telnet client, telnet proxy, and application framework created specifically to make writing code for IRE's [Achaea](http://achaea.com) fun and easy.

You might enjoy Sage if:

* You'd prefer to write your system in an IDE or text editor instead of your MUD client.
* You like Python and want to take full advantage of the language's power.
* You want your system to be client agnostic.
* Mixing code inside XML makes your nose bleed.
* You enjoy modularity and like sharing your code with others.
* You are unique and would rather build your own system than use a pre-built one.

## Features

* Twisted-based telnet proxy allowing you to connect a client of your choice.
* Full GMCP support.
* Extensive 'signal' or 'pub/sub' system for easy handling of asynchronous events.
* Powerful, fast, and easy to use triggers/aliases.
* An alternative syntax for making large numbers of triggers and aliases.
* Extensibility through add-on 'sage apps'.
* Interactive console allowing you to write live code in a running app.
* Auto-reloading of your code as you change it.

## Requirements
- Python 2.7+ (2.7.5 recommended). 3+ not yet supported.
- Unix-like operating system (OS X, Linux, BSD, etc...)

## Documentation
Go to http://astralinae.github.com/sage for a prebuilt version of the current documentation. Otherwise build them yourself from the sphinx sources in the docs folder.

## Support
Please feel free to file an issue here if you have a problem or find a bug.

You might find some helpful folks at \#astralinae on Freenode IRC.

## Contribute
1. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
2. Fork the [repository](http://github.com/astralinae/sage) on Github to start making your changes to the master branch (or branch off of it).
3. If you can, please write a test which shows that the bug was fixed or that the feature works as expected.
4. Send a pull request and bug the maintainer until it gets merged and published.
