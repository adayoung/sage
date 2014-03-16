Gamelog
=======

Gamelog simply writes the output of the game to file.
Having logs of everything you do in Achaea is incredibly useful! The logs are dated by day and roll
over at midnight automatically.

How to use
----------

1- Add gamelog to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
	'sage.contrib.apps.gamelog',
	'your other apps...'
)
```

2- That's it!

By default your logs will appear in `$HOME/sage-logs`. You can change this directory by modifying the config dictionary:

```python
# In your parent/main app
from sage.apps import gamelog
gamelog.config['log_directory'] = '/path/to/logs'
```

If you want ANSI coloring in your logs:

```python
gamelog.config['ansi'] = True
```