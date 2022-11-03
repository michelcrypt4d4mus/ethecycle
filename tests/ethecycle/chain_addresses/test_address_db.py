from ethecycle.chain_addresses.address_db import _get_or_create_data_source_id

TEST_DATA_SOURCE = '/illmatic/the_world_is_yrs'


def test_get_or_create_data_source_id():
    data_source_id = _get_or_create_data_source_id(TEST_DATA_SOURCE)
    assert data_source_id == _get_or_create_data_source_id(TEST_DATA_SOURCE)
