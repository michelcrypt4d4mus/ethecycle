import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

LOG_LEVEL = 'WARN'

console = Console()
log = logging.getLogger('ethecycle')
log.addHandler(RichHandler(rich_tracebacks=True))


def set_log_level(log_level) -> None:
    log.setLevel(log_level)

    for handler in log.handlers:
        handler.setLevel(log_level)


def print_wallet_header(wallet_address, wallet_txns):
    console.line(2)
    txt = Text('Wallet ').append(wallet_address, style='green').append(' has ')
    txt.append(str(len(wallet_txns)), style='cyan').append(' txns')
    console.print(Panel(txt, expand=False))


def print_headline(headline: str) -> None:
    console.line(2)
    console.print(Panel(headline, style='reverse', width=60))
    console.line()
