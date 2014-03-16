import logging
from logging.handlers import TimedRotatingFileHandler
from sage.signals.net import pre_outbound as outbound_signal
from sage.signals import player_connected as player_connected_signal
from sage import ansi
from datetime import datetime
import os
import sage

# log instance held here to make it easy to call from other apps
log = None

# modify the logging config from your app's init()
config = {
    'log_directory': os.path.expanduser('~') + '/sage-logs',
    'ansi': False,
    'suffix': "%Y%m%d",
    'format_ansi': ansi.grey("[%(asctime)-15s]") + " %(message)s",
    'format': "[%(asctime)-15s] %(message)s",
    'date_format': "%Y-%m-%d %H:%M:%S.%f"
}


class LogFormatter(logging.Formatter):
    """ Extend logging's Formatter to support microseconds """

    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


def post_init():
    if not os.path.exists(config['log_directory']):
        os.makedirs(config['log_directory'])


def make_filename(name):
    today = datetime.now().strftime("%Y%m%d")
    out = os.path.join(config['log_directory'])
    out += "/%s.%s" % (name, today)
    return out


# We wait for the player to login so we know the player's name
def on_connect(**kwargs):
    global log

    name = sage.player.name.lower()
    log = logging.getLogger(name)

    handler = TimedRotatingFileHandler(
        make_filename(name),
        'midnight',  # logs rotate at midnight
        0
    )

    handler.suffix = config['suffix']

    if config['ansi']:
        formatter = LogFormatter(fmt=config['format_ansi'], datefmt=config['date_format'])
        outbound_signal.connect(write_ansi)
    else:
        formatter = LogFormatter(fmt=config['format'], datefmt=config['date_format'])
        outbound_signal.connect(write_raw)

    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

player_connected_signal.connect(on_connect)


def write_ansi(**kwargs):
    for line in kwargs['lines']:
        log.debug(line.output)

    log.debug(kwargs['ansi_prompt'])

def write_raw(**kwargs):
    for line in kwargs['lines']:
        log.debug(line)

    log.debug(kwargs['prompt'])