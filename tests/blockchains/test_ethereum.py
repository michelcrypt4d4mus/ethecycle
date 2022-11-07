from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.models.token import Token
from ethecycle.util.string_constants import ETHEREUM, USDT, USDT_ETHEREUM_ADDRESS


def test_is_valid_address():
    assert Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS)
    assert not Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS + 'x')
    assert not Ethereum.is_valid_address(USDT_ETHEREUM_ADDRESS.replace('0x', '\\x'))
