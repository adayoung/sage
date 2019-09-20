# -*- coding: utf-8 -*-
"""
Helper methods for ANSI formatting and colors.

Credits for help on this file go to the Lyntin project and Django Termcolors
"""

import re

# for finding ANSI color sequences
ANSI_COLOR_REGEXP = re.compile('(' + chr(27) + '\[[0-9;]*m)')

# Used for strfcolor
CFORMAT = re.compile('[%&].')

color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
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

    :param text: string that will be colored
    :param opts: (optional) extra options
    :param \*\*kwargs: (optional) parameters such as fg and bg

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
        8 bit color codes: 0-255
        24 bit colour codes: (r, g, b)

    Valid options:
        'bold'
        'underscore'
        'blink'
        'reverse'
        'conceal'
        'noreset' - string will not be auto-terminated with the RESET code

    Examples:
        colorize('hello', fg='red', bg='blue', opts=('blink',))
        colorize('hello', fg=140)
        colorize('hello', fg=(240, 128, 128))
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
            if isinstance(v, tuple): 
                code_list.append('38;2;{};{};{}'.format(v[0], v[1], v[2]))
            elif isinstance(v, int):
                code_list.append('38;5;{}'.format(code))
            else:
                code_list.append(foreground[v])
        elif k == 'bg':
            if isinstance(v, tuple): 
                code_list.append('48;2;{};{};{}'.format(v[0], v[1], v[2]))
            elif isinstance(v, int):
                code_list.append('48;5;{}'.format(code))
            else:
                code_list.append(background[v])

    for o in opts:
        if o in opt_dict:
            code_list.insert(0, opt_dict[o])
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


def filter_ansi(text):
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

strfcolor_table = {
    '%w': '\x1b[0;37m',
    '%b': '\x1b[0;34m',
    '%r': '\x1b[0;31m',
    '%g': '\x1b[0;32m',
    '%y': '\x1b[0;33m',
    '%_': '\x1b[0;30m',
    '%m': '\x1b[0;35m',
    '%c': '\x1b[0;36m',
    '%-': '\x1b[1;30m',
    '%W': '\x1b[1;37m',
    '%R': '\x1b[1;31m',
    '%G': '\x1b[1;32m',
    '%Y': '\x1b[1;33m',
    '%B': '\x1b[1;34m',
    '%M': '\x1b[1;35m',
    '%C': '\x1b[1;36m',
    '&w': '\x1b[47m',
    '&b': '\x1b[44m',
    '&r': '\x1b[41m',
    '&g': '\x1b[42m',
    '&y': '\x1b[43m',
    '&m': '\x1b[45m',
    '&c': '\x1b[46m',
    '%0': '\x1b[0m',
    '%%': '%'
}


def repl_color(matchobj):
    key = matchobj.group(0)
    if key in strfcolor_table:
        return strfcolor_table[key]

    return matchobj.group(0)


def strfcolor(string):
    """ Format a string with a color format syntax.

    %w = white
    %b = blue
    %r = red
    %g = green
    %y = yellow
    %_ = black
    %m = magenta
    %c = cyan
    %- = grey
    %W = bold white
    %R = bold red
    %G = bold green
    %Y = bold yellow
    %B = bold blue
    %M = bold magenta
    %C = bold cyan
    &w = white backgound
    &b = blue background
    &r = red background
    &g = green background
    &y = yellow background
    &m = magenta background
    &c = cyan background
    %0 = reset
    """
    return CFORMAT.sub(repl_color, string)


# Helper methods
white = make_style(fg='white')
black = make_style(fg='black')
red = make_style(fg='red')
green = make_style(fg='green')
yellow = make_style(fg='yellow')
blue = make_style(fg='blue')
magenta = make_style(fg='magenta')
cyan = make_style(fg='cyan')
grey = make_style(fg='black', opts=('bold',))
bold_white = make_style(fg='white', opts=('bold',))
bold_red = make_style(fg='red', opts=('bold',))
bold_green = make_style(fg='green', opts=('bold',))
bold_yellow = make_style(fg='yellow', opts=('bold',))
bold_blue = make_style(fg='blue', opts=('bold',))
bold_magenta = make_style(fg='magenta', opts=('bold',))
bold_cyan = make_style(fg='cyan', opts=('bold',))
