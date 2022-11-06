from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.util.string_constants import USDT, USDT_ETHEREUM_ADDRESS



def test_token_address():
    assert Ethereum.token_address(USDT) == USDT_ETHEREUM_ADDRESS


def test_token_decimals():
    usdt_address = Ethereum.token_address(USDT)
    assert Ethereum.token_decimals(usdt_address) == 6


def test_token_symbol():
    usdt_address = Ethereum.token_address(USDT)
    assert Ethereum.token_symbol(usdt_address) == USDT


def test_is_valid_address():
    assert Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS)
    assert not Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS + 'x')
    assert not Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS.replace('0x', '\\x'))
