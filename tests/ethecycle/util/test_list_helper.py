from ethecycle.util.list_helper import has_intersection

LIST1 = "the young city bandit hold myself down singlehanded".split()


def test_has_intersection():
    assert has_intersection(LIST1, ['myself'])
    assert not has_intersection(LIST1, ['illmatic', 'part2'])
