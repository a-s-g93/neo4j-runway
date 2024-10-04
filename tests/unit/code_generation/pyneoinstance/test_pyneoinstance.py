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

standard_answer = """"neo4j":
  "uri": |-
    uri
  "user": |-
    neo4j
  "password": |-
    password
  "database": |-
    neo4j
"queries":
  "pre-load":
  - |-
    CREATE CONSTRAINT nodea_alpha IF NOT EXISTS FOR (n:NodeA) REQUIRE n.alpha IS UNIQUE;
  - |-
    CREATE CONSTRAINT nodeb_beta IF NOT EXISTS FOR (n:NodeB) REQUIRE n.beta IS UNIQUE;
  - |-
    CREATE CONSTRAINT nodec_gamma IF NOT EXISTS FOR (n:NodeC) REQUIRE n.gamma IS UNIQUE;
  "load":
    "nodes":
      "NodeA": |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeA {alpha: row.au})
      "NodeB": |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeB {beta: row.bu})
      "NodeC": |-
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeC {gamma: row.cu})
        SET n.decorator = row.dec
    "relationships":
      "REL_AC_NodeA_NodeC": |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:NodeA {alpha: row.au})
        MATCH (target:NodeC {gamma: row.cu})
        MERGE (source)-[n:REL_AC]->(target)
"""


def test_pyneoinstance_config_generation() -> None:
    gen = PyNeoInstanceConfigGenerator(
        username="neo4j",
        password="password",
        database="neo4j",
        uri="uri",
        data_model=data_model,
    )

    assert gen.generate_config_string() == standard_answer


pre_post_answer = """"neo4j":
  "uri": |-
    uri
  "user": |-
    neo4j
  "password": |-
    password
  "database": |-
    neo4j
"queries":
  "pre-load":
  - |-
    CREATE CONSTRAINT nodea_alpha IF NOT EXISTS FOR (n:NodeA) REQUIRE n.alpha IS UNIQUE;
  - |-
    CREATE CONSTRAINT nodeb_beta IF NOT EXISTS FOR (n:NodeB) REQUIRE n.beta IS UNIQUE;
  - |-
    CREATE CONSTRAINT nodec_gamma IF NOT EXISTS FOR (n:NodeC) REQUIRE n.gamma IS UNIQUE;
  - |-
    CREATE INDEX test
  - |-
    CREATE INDEX test2
  "load":
    "nodes":
      "NodeA": |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeA {alpha: row.au})
      "NodeB": |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeB {beta: row.bu})
      "NodeC": |-
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:NodeC {gamma: row.cu})
        SET n.decorator = row.dec
    "relationships":
      "REL_AC_NodeA_NodeC": |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:NodeA {alpha: row.au})
        MATCH (target:NodeC {gamma: row.cu})
        MERGE (source)-[n:REL_AC]->(target)
  "post-load":
  - |-
    CREATE (n:Test)
    SET n.test = 'test'
"""
pre_ingest = """CREATE INDEX test;
CREATE INDEX test2;"""
post_ingest = """CREATE (n:Test)
SET n.test = 'test';"""


def test_pyneoinstance_config_with_pre_and_post_ingest() -> None:
    gen = PyNeoInstanceConfigGenerator(
        username="neo4j",
        password="password",
        database="neo4j",
        uri="uri",
        data_model=data_model,
        pre_ingest_code=pre_ingest,
        post_ingest_code=post_ingest,
    )

    print(gen.generate_config_string())
    assert gen.generate_config_string() == pre_post_answer
