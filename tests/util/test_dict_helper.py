from ethecycle.util.dict_helper import walk_json


TEST_DICT = {
    'dict_key1': {
        'inner_key2': 'inner_key3',
        'inner_num_key': 5
    },
    'array_key': [
        'array_element_1',
        'array_element_2',
    ],
    'str_key1': '0x1234'
}


def test_walk_json():
    results = [(a, b) for (a, b) in walk_json(TEST_DICT)]

    assert(results == [
        ('dict_key1.inner_key2', 'inner_key3'),
        ('array_key.0', 'array_element_1'),
        ('array_key.1', 'array_element_2'),
        ('str_key1', '0x1234')
    ])
