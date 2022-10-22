import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

LOG_LEVEL = 'WARN'

console = Console()


def set_log_level(log_level) -> None:
    log.setLevel(LOG_LEVEL)
    log.handlers[0].setLevel(LOG_LEVEL)


log = logging.getLogger('ethecycle')
log.addHandler(RichHandler(rich_tracebacks=True))


def print_wallet_header(wallet_address, wallet_txns):
    console.line(2)
    txt = Text('Wallet ').append(wallet_address, style='green').append(' has ')
    txt.append(str(len(wallet_txns)), style='cyan').append(' txns')
    console.print(Panel(txt, expand=False))
