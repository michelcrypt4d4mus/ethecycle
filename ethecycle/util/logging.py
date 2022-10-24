"""
Logging and printing, for now.
"""
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

### Logging ###
LOG_LEVEL = 'WARN'

console = Console()
log = logging.getLogger('ethecycle')
log.addHandler(RichHandler(rich_tracebacks=True))


def set_log_level(log_level) -> None:
    log.setLevel(log_level)

    for handler in log.handlers:
        handler.setLevel(log_level)


### Printing ###
BYTES = 'color(100) dim'
BYTES_NO_DIM = 'color(100)'
BYTES_BRIGHTEST = 'color(220)'
BYTES_BRIGHTER = 'orange1'
BYTES_HIGHLIGHT = 'color(136)'
DARK_GREY = 'color(236)'
GREY = 'color(241)'
GREY_ADDRESS = 'color(238)'
PEACH = 'color(215)'
PURPLE = 'color(20)'

COLOR_THEME_DICT = {
    # colors
    'dark_orange': 'color(58)',
    'grey': GREY,
    'grey.dark': DARK_GREY,
    'grey.dark_italic': f"{DARK_GREY} italic",
    'grey.darker_italic': 'color(8) dim italic',
    'grey.darkest': 'color(235) dim',
    'grey.light': 'color(248)',
    'off_white': 'color(245)',
    # data types
    'benchmark': BYTES,
    'number': 'cyan',
    'purple_grey': "color(60) dim italic",
    # bytes
    'ascii': 'color(58)',
    'ascii_unprintable': 'color(131)',
    'bytes': BYTES,
    'bytes.title_dim': 'orange1 dim',
    'bytes.title': BYTES_BRIGHTER,
    'bytes.decoded': BYTES_BRIGHTEST,
    'error': 'bright_red',
}

COLOR_THEME = Theme(COLOR_THEME_DICT)

console = Console(theme=COLOR_THEME, color_system='256')


def print_wallet_header(wallet_address, wallet_txns):
    console.line(2)
    txt = Text('Wallet ').append(wallet_address, style='green').append(' has ')
    txt.append(str(len(wallet_txns)), style='cyan').append(' txns')
    console.print(Panel(txt, expand=False))


def print_headline(headline: str) -> None:
    console.line(2)
    console.print(Panel(headline, style='reverse', width=60))
    console.line()
