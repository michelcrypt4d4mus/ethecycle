import pytest

from ethecycle.models.address import get_chain_info
from ethecycle.util.string_constants import USDT, USDT_ETHEREUM_ADDRESS


@pytest.fixture
def generic_chain_info():
    return get_chain_info('crypto bro incorporated')


def test_is_valid_address(generic_chain_info):
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS)
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS + 'x')
    assert generic_chain_info.is_valid_address(USDT_ETHEREUM_ADDRESS.replace('0x', '\\x'))
    assert not generic_chain_info.is_valid_address('xyz')
