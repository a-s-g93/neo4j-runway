import unittest

from neo4j_runway.code_generation import PyIngestConfigGenerator
from neo4j_runway.models import DataModel, Node, Property, Relationship

nodes = [
    Node(
        label="NodeA",
        properties=[
            Property(name="alpha", type="str", csv_mapping="au", is_unique=True)
        ],
        csv_name="CSV_A.csv",
    ),
    Node(
        label="NodeB",
        properties=[
            Property(name="beta", type="str", csv_mapping="bu", is_unique=True)
        ],
        csv_name="CSV_B.csv",
    ),
    Node(
        label="NodeC",
        properties=[
            Property(name="gamma", type="str", csv_mapping="cu", is_unique=True),
            Property(name="decorator", type="str", csv_mapping="dec", is_unique=False),
        ],
        csv_name="CSV_A.csv",
    ),
]
rel = Relationship(
    type="REL_AC", source="NodeA", target="NodeC", properties=[], csv_name="CSV_A.csv"
)

data_model = DataModel(nodes=nodes, relationships=[rel])


class TestPyIngestGenerationWithParams(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pyingest_config = {
            "CSV_A.csv": {
                "field_separator": "|",
                "skip_file": False,
                "skip_records": 5,
            },
            "CSV_B.csv": {"skip_file": True, "batch_size": 1234},
        }
        cls.gen = PyIngestConfigGenerator(
            data_model=data_model,
            file_directory="./",
            pyingest_file_config=pyingest_config,
        )

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
  field_separator: '|'
  skip_file: false
  skip_records: 5
  url: $BASE/./CSV_A.csv
- chunk_size: 1234
  cql: |
    WITH $dict.rows AS rows
    UNWIND rows AS row
    MERGE (n:NodeB {beta: row.bu})
  skip_file: true
  url: $BASE/./CSV_B.csv
- chunk_size: 100
  cql: |-
    WITH $dict.rows AS rows
    UNWIND rows AS row
    MERGE (n:NodeC {gamma: row.cu})
    SET n.decorator = row.dec
  field_separator: '|'
  skip_file: false
  skip_records: 5
  url: $BASE/./CSV_A.csv
- chunk_size: 100
  cql: |
    WITH $dict.rows AS rows
    UNWIND rows as row
    MATCH (source:NodeA {alpha: row.au})
    MATCH (target:NodeC {gamma: row.cu})
    MERGE (source)-[n:REL_AC]->(target)
  field_separator: '|'
  skip_file: false
  skip_records: 5
  url: $BASE/./CSV_A.csv
"""

if __name__ == "__main__":
    unittest.main()
