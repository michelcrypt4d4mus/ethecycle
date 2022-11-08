from ethecycle.util.number_helper import usd_string


def test_usd_string():
    assert usd_string(1000000) == "$1.0M"
    assert usd_string(386000) == '$386.0k'
    assert usd_string(555555555) == '$555.6M'
    assert usd_string(5555555555) == '$5.6 billion'
