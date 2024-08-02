import unittest

from neo4j_runway.code_generation import PyIngestConfigGenerator
from neo4j_runway.models import DataModel, Node, Property, Relationship
from tests.resources.answers.ingestion_generation_answers import *

nodes = [
    Node(
        label="NodeA",
        properties=[
            Property(name="alpha", type="str", csv_mapping="au", is_unique=True)
        ],
        csv_name="CSV_A",
    ),
    Node(
        label="NodeB",
        properties=[
            Property(name="beta", type="str", csv_mapping="bu", is_unique=True)
        ],
        csv_name="CSV_B",
    ),
    Node(
        label="NodeC",
        properties=[
            Property(name="gamma", type="str", csv_mapping="cu", is_unique=True),
            Property(name="decorator", type="str", csv_mapping="dec", is_unique=False),
        ],
        csv_name="CSV_A",
    ),
]
rel = Relationship(
    type="REL_AC", source="NodeA", target="NodeC", properties=[], csv_name="CSV_A"
)

data_model = DataModel(nodes=nodes, relationships=[rel])


class TestPyIngestGenerationMultiCSV(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = PyIngestConfigGenerator(data_model=data_model, file_directory="./")

    def test_code_generation_for_multi_csv(self) -> None:
        """
        Test the code generation for a data model with data from multiple CSVs.
        """

        self.maxDiff = None
        res = self.gen.generate_config_string()
        self.assertEqual(res, ans)


ans = """server_uri: None
admin_user: None
admin_pass: None
database: None
basepath: ./

pre_ingest:
  - CREATE CONSTRAINT nodea_alpha IF NOT EXISTS FOR (n:NodeA) REQUIRE n.alpha IS UNIQUE;
  - CREATE CONSTRAINT nodeb_beta IF NOT EXISTS FOR (n:NodeB) REQUIRE n.beta IS UNIQUE;
  - CREATE CONSTRAINT nodec_gamma IF NOT EXISTS FOR (n:NodeC) REQUIRE n.gamma IS UNIQUE;
files:
- chunk_size: 100
  cql: |
    WITH $dict.rows AS rows
    UNWIND rows AS row
    MERGE (n:NodeA {alpha: row.au})
  url: $BASE/./CSV_A.csv
- chunk_size: 100
  cql: |
    WITH $dict.rows AS rows
    UNWIND rows AS row
    MERGE (n:NodeB {beta: row.bu})
  url: $BASE/./CSV_B.csv
- chunk_size: 100
  cql: |-
    WITH $dict.rows AS rows
    UNWIND rows AS row
    MERGE (n:NodeC {gamma: row.cu})
    SET n.decorator = row.dec
  url: $BASE/./CSV_A.csv
- chunk_size: 100
  cql: |
    WITH $dict.rows AS rows
    UNWIND rows as row
    MATCH (source:NodeA {alpha: row.au})
    MATCH (target:NodeC {gamma: row.cu})
    MERGE (source)-[n:REL_AC]->(target)
  url: $BASE/./CSV_A.csv
"""

if __name__ == "__main__":
    unittest.main()
