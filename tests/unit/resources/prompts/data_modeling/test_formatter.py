from neo4j_runway.resources.prompts.data_modeling.formatters import (
    format_corrections,
    format_data_dictionary,
    format_data_model,
    format_discovery,
    format_entity_pool,
    format_errors,
    format_use_cases,
    format_valid_columns,
)


def test_data_dictionary_formatter_multifile() -> None:
    dd = {"a.csv": {"a": "test", "b": "test2"}, "b.csv": {"a": "test", "b": "test2"}}
    res = """a.csv
  * a : test
  * b : test2
b.csv
  * a : test
  * b : test2

"""
    string = format_data_dictionary(data_dictionary=dd, multifile=True)

    assert res in string


def test_data_dictionary_formatter_singlefile() -> None:
    dd = {"file": {"a": "test", "b": "test2"}}

    string = format_data_dictionary(data_dictionary=dd, multifile=False)

    assert "The following is a description of each feature in the data:\n" in string


def test_data_model_formatter_with_yaml() -> None: ...


def test_data_formatter_without_yaml() -> None: ...


def test_discovery_formatter() -> None: ...


def test_entity_pool_formatter() -> None: ...


def test_error_formatter() -> None:
    errors = ["bad", "worse"]
    answer = """Errors:
* bad
* worse
"""
    assert format_errors(errors=errors) == answer


def test_use_cases_formatter() -> None: ...


def test_user_corrections_formatter() -> None: ...


def test_valid_columns_formatter() -> None: ...
