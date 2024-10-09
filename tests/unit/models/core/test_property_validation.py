from neo4j_runway.models.core.property import Property


def test_unique_and_node_key() -> None:
    """should auto make `part_of_key` False if `is_unique` True"""

    p = Property(
        name="test", type="str", column_mapping="col1", is_unique=True, part_of_key=True
    )

    assert not p.part_of_key
