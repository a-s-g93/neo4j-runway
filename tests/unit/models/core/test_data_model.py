import pytest
from pydantic import ValidationError

from neo4j_runway.models import DataModel, Node, Property, Relationship
from tests.resources.answers.data_model_yaml import data_model_dict, data_model_yaml

columns = [
    "name",
    "age",
    "street",
    "city",
    "pet_name",
    "pet",
    "toy",
    "toy_type",
]

person_name = Property(
    name="name", type="str", column_mapping="name", is_unique=True, alias="knows"
)
person_age = Property(name="age", type="str", column_mapping="age", is_unique=False)
address_street = Property(
    name="street",
    type="str",
    column_mapping="street",
    is_unique=False,
    part_of_key=True,
)
address_city = Property(
    name="city", type="str", column_mapping="city", is_unique=False, part_of_key=True
)
pet_name = Property(name="name", type="str", column_mapping="pet_name", is_unique=True)
pet_kind = Property(name="kind", type="str", column_mapping="pet", is_unique=False)
toy_name = Property(name="name", type="str", column_mapping="toy", is_unique=True)
toy_kind = Property(name="kind", type="str", column_mapping="toy_type", is_unique=False)

good_nodes = [
    Node(
        label="Person",
        properties=[person_name, person_age],
    ),
    Node(
        label="Address",
        properties=[address_street, address_city],
    ),
    Node(
        label="Pet",
        properties=[pet_name, pet_kind],
    ),
    Node(
        label="Toy",
        properties=[toy_name, toy_kind],
    ),
]

good_relationships = [
    Relationship(
        type="HAS_ADDRESS",
        properties=[],
        source="Person",
        target="Address",
    ),
    Relationship(
        type="KNOWS",
        properties=[],
        source="Person",
        target="Person",
    ),
    Relationship(
        type="HAS_PET",
        properties=[],
        source="Person",
        target="Pet",
    ),
    Relationship(
        type="PLAYS_WITH",
        properties=[],
        source="Pet",
        target="Toy",
    ),
]
bad_relationships = good_relationships + [
    Relationship(
        type="BAD",
        properties=[],
        source="Dog",
        target="Toy",
    )
]
bad_nodes = good_nodes + [
    Node(
        label="Toy",
        properties=[toy_name, toy_kind],
    )
]


def test_bad_init() -> None:
    """
    Test bad input for init.
    """

    with pytest.raises(ValidationError) as e:
        DataModel(nodes=bad_nodes, relationships=bad_relationships)


def test_good_init() -> None:
    """
    This input should pass.
    """

    # valid
    assert isinstance(
        DataModel(nodes=good_nodes, relationships=good_relationships),
        DataModel,
    )


def test_to_dict() -> None:
    """
    Test model_dump property.
    """

    test_model = DataModel(nodes=good_nodes, relationships=good_relationships)

    test_dict = test_model.model_dump()

    assert list(test_dict.keys()) == ["nodes", "relationships", "metadata"]
    assert list(test_dict["nodes"][0].keys()) == ["label", "properties", "source_name"]
    assert list(test_dict["relationships"][0].keys()) == [
        "type",
        "properties",
        "source",
        "target",
        "source_name",
    ]


def test_neo4j_naming_conventions_used() -> None:
    """
    Test renaming labels, types and properties to Neo4j naming conventions.
    """

    prop1 = {
        "name": "Name",
        "type": "str",
        "column_mapping": "name",
        "alias": "knows_person",
        "is_unique": True,
    }
    prop2 = {
        "name": "person_age",
        "type": "int",
        "column_mapping": "age",
        "is_unique": False,
    }
    prop3 = {
        "name": "CurrentStreet",
        "type": "str",
        "column_mapping": "street",
        "is_unique": True,
    }
    prop4 = {
        "name": "favorite_score",
        "type": "int",
        "column_mapping": "favorite",
        "is_unique": False,
    }

    name_conv_nodes = [
        {
            "label": "person",
            "properties": [prop1, prop2],
        },
        {
            "label": "current_Address",
            "properties": [prop3],
        },
    ]

    name_conv_relationships = [
        {
            "type": "has_address",
            "properties": [prop4],
            "source": "Person",
            "target": "current_address",
        },
        {
            "type": "HasSecondAddress",
            "source": "person",
            "target": "current_Address",
        },
        {
            "type": "hasAddress_Three",
            "source": "Person",
            "target": "CURRENT_ADDRESS",
        },
    ]

    dm = DataModel.model_validate(
        {"nodes": name_conv_nodes, "relationships": name_conv_relationships},
        context={"allow_parallel_relationships": True},
    )

    assert set(dm.node_labels) == {"Person", "CurrentAddress"}
    assert set(dm.relationship_types) == {
        "HAS_ADDRESS",
        "HAS_SECOND_ADDRESS",
        "HAS_ADDRESS_THREE",
    }

    for rel in dm.relationships:
        assert rel.source in ["Person", "CurrentAddress"]
        assert rel.target in ["Person", "CurrentAddress"]


def test_neo4j_naming_conventions_ignored() -> None:
    prop1 = {
        "name": "Name",
        "type": "str",
        "column_mapping": "name",
        "alias": "knows_person",
        "is_unique": True,
    }

    prop3 = {
        "name": "CurrentStreet",
        "type": "str",
        "column_mapping": "street",
        "is_unique": True,
    }

    name_conv_nodes = [
        {
            "label": "person",
            "properties": [prop1],
        },
        {
            "label": "current_address",
            "properties": [prop3],
        },
    ]

    name_conv_relationships = [
        {
            "type": "has_address",
            "source": "person",
            "target": "current_address",
        }
    ]

    dm = DataModel.model_validate(
        {"nodes": name_conv_nodes, "relationships": name_conv_relationships},
        context={"apply_neo4j_naming_conventions": False},
    )

    assert set(dm.node_labels) == {"person", "current_address"}
    assert set(dm.relationship_types) == {"has_address"}

    for rel in dm.relationships:
        assert rel.source in ["person", "current_address"]
        assert rel.target in ["person", "current_address"]


def test_from_arrows_init() -> None:
    """
    Test init from arrows json file.
    """

    data_model = DataModel.from_arrows(
        file_path="tests/resources/data_models/arrows-data-model.json"
    )

    assert data_model.nodes[0].properties[0].is_unique
    assert data_model.nodes[0].properties[1].type == "int"
    assert data_model.nodes[0].label == "Person"


def test_to_yaml_string() -> None:
    """
    Test data model output to yaml format string.
    """

    data_model = DataModel(
        nodes=data_model_dict["nodes"],
        relationships=data_model_dict["relationships"],
    )

    maxDiff = None
    assert data_model.to_yaml(write_file=False) == data_model_yaml


def test_data_model_with_multi_csv_from_arrows() -> None:
    data_model = DataModel.from_arrows(
        "tests/resources/data_models/people-pets-arrows-multi-csv.json"
    )

    assert data_model.relationships[-1].source_name == "shelters.csv"
    assert data_model.relationships[0].source_name == "pets-arrows.csv"
    assert data_model.nodes[0].source_name == "pets-arrows.csv"


def test_data_model_with_multi_csv_from_solutions_workbench() -> None:
    pass
