# -*- coding: utf-8 -*-
"""
sage.ansi
~~~~~~~~~

Helper methods for ANSI formatting and colors.

This is hardly compliant to the standard. Please don't use this for anything
but Achaea.

A sage color tuple works in this format:
    (bright/bold, foreground, background, underline)

We don't support other (less-supported) options like blink, etc.

Credits for help on this file go to the Lyntin project and Django Termcolors
"""

import re

# for finding ANSI color sequences
ANSI_COLOR_REGEXP = re.compile('(' + chr(27) + '\[[0-9;]*m)')

color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', \
    'white')
foreground = dict([(color_names[x], '3%s' % x) for x in range(8)])
background = dict([(color_names[x], '4%s' % x) for x in range(8)])
opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

RESET = '0'


def colorize(text='', opts=(), **kwargs):
    """
    Returns your text, enclosed in ANSI graphics codes.

    Depends on the keyword arguments 'fg' and 'bg', and the contents of
    the opts tuple/list.

    Returns the RESET code if no parameters are given.

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

    Valid options:
        'bold'
        'underscore'
        'blink'
        'reverse'
        'conceal'
        'noreset' - string will not be auto-terminated with the RESET code

    Examples:
        colorize('hello', fg='red', bg='blue', opts=('blink',))
        colorize()
        colorize('goodbye', opts=('underscore',))
        print(colorize('first line', fg='red', opts=('noreset',)))
        print('this should be red too')
        print(colorize('and so should this'))
        print('this should not be red')
    """
    code_list = []
    if text == '' and len(opts) == 1 and opts[0] == 'reset':
        return '\x1b[%sm' % RESET
    for k, v in kwargs.iteritems():
        if k == 'fg':
            code_list.append(foreground[v])
        elif k == 'bg':
            code_list.append(background[v])
    for o in opts:
        if o in opt_dict:
            code_list.append(opt_dict[o])
    if 'noreset' not in opts:
        text = text + '\x1b[%sm' % RESET
    return ('\x1b[%sm' % ';'.join(code_list)) + text


def make_style(opts=(), **kwargs):
    """
    Returns a function with default parameters for colorize()

    Example:
        bold_red = make_style(opts=('bold',), fg='red')
        print(bold_red('hello'))
        KEYWORD = make_style(fg='yellow')
        COMMENT = make_style(fg='blue', opts=('bold',))
    """
    return lambda text: colorize(text, opts, **kwargs)


def filter(text):
    """ Takes in text and filters out the ANSI color codes. """

    return ANSI_COLOR_REGEXP.sub('', text)


def split(text):
    """ Splits text and ANSI color sequences """

    return ANSI_COLOR_REGEXP.split(text)


def split_expanded(text):
    """ Split a string into string parts and tuples of color sequences """

    processed = list()
    parts = split(text)

    for part in parts:
        if len(part) == 0:
            continue

        if part[0] != chr(27):
            processed.append(part)
            continue

        # we make the ridiculous assumption anything not defined as X;X is 0;X
        if ';' not in part:
            code = '0;' + part[2:-1]
        else:
            code = part[2:-1]

        processed.append(code)

    return processed

# Helper methods
white = make_style(fg='white')
black = make_style(fg='black')
red = make_style(fg='red')
green = make_style(fg='green')
yellow = make_style(fg='yellow')
blue = make_style(fg='blue')
magenta = make_style(fg='magenta')
cyan = make_style(fg='cyan')
bold_white = make_style(fg='white', opts=('bold',))
