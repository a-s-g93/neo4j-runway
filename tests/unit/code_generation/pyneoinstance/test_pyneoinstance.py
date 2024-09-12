from neo4j_runway.code_generation.pyneoinstance.pyneoinstance_generator import (
    PyNeoInstanceConfigGenerator,
)
from neo4j_runway.models.core import DataModel, Node, Property, Relationship

nodes = [
    Node(
        label="NodeA",
        properties=[
            Property(name="alpha", type="str", column_mapping="au", is_unique=True)
        ],
        source_name="CSV_A.csv",
    ),
    Node(
        label="NodeB",
        properties=[
            Property(name="beta", type="str", column_mapping="bu", is_unique=True)
        ],
        source_name="CSV_B.csv",
    ),
    Node(
        label="NodeC",
        properties=[
            Property(name="gamma", type="str", column_mapping="cu", is_unique=True),
            Property(
                name="decorator", type="str", column_mapping="dec", is_unique=False
            ),
        ],
        source_name="CSV_A.csv",
    ),
]
rel = Relationship(
    type="REL_AC",
    source="NodeA",
    target="NodeC",
    properties=[],
    source_name="CSV_A.csv",
)

data_model = DataModel(nodes=nodes, relationships=[rel])


def test_pyneoinstance_config_generation() -> None:
    gen = PyNeoInstanceConfigGenerator(
        username="neo4j",
        password="password",
        database="neo4j",
        uri="uri",
        data_model=data_model,
    )
    print(gen.generate_config_string())
