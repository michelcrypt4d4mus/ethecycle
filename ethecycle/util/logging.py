"""
Logging and printing, for now.
"""
import logging
import time
from sys import exit

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

from ethecycle.config import Config
from ethecycle.util.string_constants import DEBUG, ETHECYCLE

### Logging ###
LOG_LEVEL = 'WARN'


def set_log_level(log_level) -> None:
    log.setLevel(log_level)

    for handler in log.handlers:
        handler.setLevel(log_level)


log = logging.getLogger(ETHECYCLE)
log.addHandler(RichHandler(rich_tracebacks=True))

if Config.debug:
    set_log_level(DEBUG)
else:
    set_log_level('INFO')


### Printing ###
BYTES = 'color(100) dim'
BYTES_NO_DIM = 'color(100)'
BYTES_BRIGHTEST = 'color(220)'
BYTES_BRIGHTER = 'orange1'
BYTES_HIGHLIGHT = 'color(136)'
DARK_GREY = 'color(236)'
GREY = 'color(239)'
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
    'benchmark': 'color(180) dim',
    'benchmark.indent': BYTES,
    'number': 'cyan',
    'purple_grey': "color(60) dim italic",
    'cql': PEACH,
    # bytes
    'ascii': 'color(58)',
    'ascii_unprintable': 'color(131)',
    'bytes': BYTES,
    'bytes.title_dim': 'orange1 dim',
    'bytes.title': BYTES_BRIGHTER,
    'bytes.decoded': BYTES_BRIGHTEST,
    'error': 'bright_red',
    'possibility': 'color(132)',
}

COLOR_THEME = Theme(COLOR_THEME_DICT)
INDENT_SPACES = 4
console = Console(theme=COLOR_THEME, color_system='256')


def print_dim(msg) -> None:
    console.print(msg, style='dim')


def print_wallet_header(wallet_address, wallet_txns):
    console.line(2)
    txt = Text('Wallet ').append(wallet_address, style='green').append(' has ')
    txt.append(str(len(wallet_txns)), style='cyan').append(' txns')
    console.print(Panel(txt, expand=False))


def print_headline(headline: str) -> None:
    console.line(2)
    console.print(Panel(headline, style='reverse', width=60))
    console.line()


def print_indented(msg: str, style: str = '', indent_level: int = 1) -> None:
    console.print(f"{indent_whitespace(indent_level)}{msg}", style=style)


def print_benchmark(msg: str, start_time: float, indent_level: int = 1, style:str = 'benchmark') -> float:
    """Print benchmark message and return duration since 'start_time' argument."""
    duration = time.perf_counter() - start_time
    indent = ' ' * 4 * indent_level
    style = style if indent_level < 2 else 'benchmark.indent'
    console.print(f"{indent}{msg} in {duration:02.2f} seconds...", style=style)
    return duration


def print_address_import(msg: str) -> None:
    console.print(f"Importing {msg} chain addresses...", style='magenta')


def ask_for_confirmation(msg: Text) -> None:
    """Primitive user confirmation"""
    console.print(msg.append("\n('y' to continue, any other key to exit)", style='white dim'))

    if input().lower() != 'y':
        exit()


def indent_whitespace(indent_level: int = 1):
    return ' ' * INDENT_SPACES * indent_level
