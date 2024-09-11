from neo4j_runway.models import DataModel, Node, Property, Relationship

data_dictionary = {
    "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
    "b.csv": {"id": "unique id for b", "a_id": "unique id for a.", "c": "feature c"},
}

valid_columns = {k: list(v.keys()) for k, v in data_dictionary.items()}

nodes = [
    Node(
        label="LabelA",
        properties=[
            Property(
                name="id",
                type="str",
                column_mapping="id",
                alias="a_id",
                is_unique=True,
            ),
            Property(name="b", type="str", column_mapping="b"),
        ],
        source_name="a.csv",
    ),
    Node(
        label="LabelB",
        properties=[
            Property(name="id", type="str", column_mapping="id", is_unique=True),
            Property(name="c", type="str", column_mapping="c"),
        ],
        source_name="b.csv",
    ),
]

data_model = DataModel(
    nodes=nodes,
    relationships=[
        Relationship(
            type="HAS_REL", source="LabelA", target="LabelB", source_name="b.csv"
        )
    ],
)
data_model_flipped = DataModel(
    nodes=nodes,
    relationships=[
        Relationship(
            type="HAS_REL", source="LabelB", target="LabelA", source_name="b.csv"
        )
    ],
)


def test_multi_file_different_source_relationship_valid_source_node() -> None:
    validation = data_model.validate_model(
        valid_columns=valid_columns, data_dictionary=data_dictionary
    )
    for e in validation["errors"]:
        print(e)
    assert len(validation["errors"]) == 0


def test_multi_file_different_source_relationship_valid_target_node() -> None:
    validation = data_model_flipped.validate_model(
        valid_columns=valid_columns, data_dictionary=data_dictionary
    )
    for e in validation["errors"]:
        print(e)
    assert len(validation["errors"]) == 0


def test_multi_file_different_source_relationship_invalid() -> None:
    data_dictionary_bad = {
        "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
        "b.csv": {"id": "unique id for b", "c": "feature c"},
    }

    valid_columns_bad = {k: list(v.keys()) for k, v in data_dictionary_bad.items()}
    validation = data_model.validate_model(
        valid_columns=valid_columns_bad, data_dictionary=data_dictionary_bad
    )

    assert len(validation["errors"]) == 1


def test_allow_duplicate_properties_true() -> None:
    data_dictionary = {
        "a.csv": {
            "id": "unique id for a. Has alias a_id",
            "b": "feature b",
            "id2": "unique id2",
        },
    }

    valid_columns = {k: list(v.keys()) for k, v in data_dictionary.items()}

    nodes_dups = [
        Node(
            label="LabelA",
            properties=[
                Property(
                    name="id",
                    type="str",
                    column_mapping="id",
                    is_unique=True,
                ),
                Property(name="b", type="str", column_mapping="b"),
            ],
            source_name="a.csv",
        ),
        Node(
            label="LabelB",
            properties=[
                Property(name="id2", type="str", column_mapping="id2", is_unique=True),
                Property(name="b", type="str", column_mapping="b"),
            ],
            source_name="a.csv",
        ),
    ]

    data_model_with_dups = DataModel(
        nodes=nodes_dups,
        relationships=[
            Relationship(
                type="HAS_REL", source="LabelA", target="LabelB", source_name="a.csv"
            )
        ],
    )

    assert data_model_with_dups.validate_model(
        data_dictionary=data_dictionary,
        valid_columns=valid_columns,
        allow_duplicate_properties=True,
    )["valid"]


def test_allow_duplicate_properties_false() -> None:
    data_dictionary = {
        "a.csv": {
            "id": "unique id for a. Has alias a_id",
            "b": "feature b",
            "id2": "unique id2",
        },
    }

    valid_columns = {k: list(v.keys()) for k, v in data_dictionary.items()}

    nodes_dups = [
        Node(
            label="LabelA",
            properties=[
                Property(
                    name="id",
                    type="str",
                    column_mapping="id",
                    is_unique=True,
                ),
                Property(name="b", type="str", column_mapping="b"),
            ],
            source_name="a.csv",
        ),
        Node(
            label="LabelB",
            properties=[
                Property(name="id2", type="str", column_mapping="id2", is_unique=True),
                Property(name="b", type="str", column_mapping="b"),
            ],
            source_name="a.csv",
        ),
    ]

    data_model_with_dups = DataModel(
        nodes=nodes_dups,
        relationships=[
            Relationship(
                type="HAS_REL", source="LabelA", target="LabelB", source_name="a.csv"
            )
        ],
    )

    assert not data_model_with_dups.validate_model(
        data_dictionary=data_dictionary,
        valid_columns=valid_columns,
        allow_duplicate_properties=False,
    )["valid"]
