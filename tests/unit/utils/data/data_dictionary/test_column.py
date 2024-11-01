from typing import Any, Dict

import pytest

from neo4j_runway.utils.data.data_dictionary.column import Column


def test_init_name_only() -> None:
    c = Column(name="col_a")

    assert c.name == "col_a"
    assert not c.primary_key
    assert not c.foreign_key


def test_init_primary_and_foreign_key() -> None:
    with pytest.raises(ValueError):
        Column(name="col_a", primary_key=True, foreign_key=True)


def test_init_invalid_python_type() -> None:
    with pytest.raises(ValueError):
        Column(name="col_a", python_type="STRING")


def test_init_nullable_and_primary_key() -> None:
    c = Column(name="col_a", primary_key=True, nullable=True)

    assert not c.nullable
    assert c.primary_key


def test_init_nullable_and_foreign_key() -> None:
    c = Column(name="col_a", foreign_key=True, nullable=True)

    assert not c.nullable
    assert c.foreign_key


def test_init_valid_aliases(validation_info_context: Dict[str, Any]) -> None:
    c = Column.model_validate(
        {"name": "col_a", "aliases": ["col_a_alias"]}, context=validation_info_context
    )

    assert "col_a_alias" in c.aliases


def test_init_invalid_aliases(validation_info_context: Dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        Column.model_validate(
            {"name": "col_a", "aliases": ["col_b_alias"]},
            context=validation_info_context,
        )


def test_init_aliases_no_context() -> None:
    c = Column.model_validate(
        {"name": "col_a", "aliases": ["col_a_alias"]}, context=dict()
    )

    assert "col_a_alias" in c.aliases


def test_compact_dict_with_ignore() -> None:
    c = Column(
        name="col_a",
        primary_key=False,
        nullable=True,
        python_type="str",
        description="a description",
        ignore=True,
    )
    assert c.compact_dict[c.name] == "a description | ignore"


def test_compact_dict_with_aliases() -> None:
    c = Column(
        name="col_a",
        primary_key=False,
        nullable=True,
        python_type="str",
        description="a description",
        aliases=["col_a_alias"],
    )
    assert c.compact_dict[c.name] == "a description Has aliases: ['col_a_alias']"
