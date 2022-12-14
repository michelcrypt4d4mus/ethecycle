from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import _get_or_create_data_source_id
from ethecycle.models.wallet import Wallet

TEST_DATA_SOURCE = '/illmatic/the_world_is_yrs'


def test_get_or_create_data_source_id():
    data_source_id = _get_or_create_data_source_id(TEST_DATA_SOURCE)
    assert data_source_id == _get_or_create_data_source_id(TEST_DATA_SOURCE)


def test_known_wallets(prep_db):
    assert Wallet.name_at_address(Ethereum.chain_string(), '0x6eff3372fa352b239bb24ff91b423a572347000d') == 'BIKI.com'
