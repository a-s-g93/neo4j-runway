from neo4j_runway.utils._utils.dictionary import get_dictionary_depth


def test_get_dictionary_depth_equals_1() -> None:
    d = {"a": "b", "1": "2"}

    assert get_dictionary_depth(d) == 1


def test_get_dictionary_depth_equals_2() -> None:
    d = {"a": {"c": "d"}, "1": {"2": "3"}}

    assert get_dictionary_depth(d) == 2


def test_get_dictionary_depth_equals_3() -> None:
    d = {"a": {"c": {"d": "e"}}, "1": {"2": {"3": "4"}}}

    assert get_dictionary_depth(d) == 3
