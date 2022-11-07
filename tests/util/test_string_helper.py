from ethecycle.util.string_helper import strip_and_set_empty_string_to_none


def test_strip_and_set_empty_string_to_none():
    assert strip_and_set_empty_string_to_none('   w ') == 'w'
    assert strip_and_set_empty_string_to_none('     ') is None
    assert strip_and_set_empty_string_to_none(5.5) == 5.5
