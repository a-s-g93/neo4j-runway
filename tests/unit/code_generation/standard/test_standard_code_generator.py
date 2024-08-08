import os
import unittest

from neo4j_runway.code_generation import StandardCypherCodeGenerator
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


class TestStandardCypherCodeGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = StandardCypherCodeGenerator(data_model=data_model)

    def test_cypher_string_generation(self) -> None:
        res = self.gen.generate_cypher_string()

        self.assertIsInstance(res, str)
        self.assertIn("NodeA", res)
        self.assertIn("NodeB", res)
        self.assertIn("NodeC", res)
        self.assertIn("REL_AC", res)

    def test_constraints_string_generation(self) -> None:
        res = self.gen.generate_constraints_string()

        self.assertIsInstance(res, str)
        self.assertIn(
            "CREATE CONSTRAINT nodea_alpha IF NOT EXISTS FOR (n:NodeA) REQUIRE n.alpha IS UNIQUE;",
            res,
        )
        self.assertIn(
            "CREATE CONSTRAINT nodeb_beta IF NOT EXISTS FOR (n:NodeB) REQUIRE n.beta IS UNIQUE;",
            res,
        )
        self.assertIn(
            "CREATE CONSTRAINT nodec_gamma IF NOT EXISTS FOR (n:NodeC) REQUIRE n.gamma IS UNIQUE;",
            res,
        )

    def test_write_cypher_file(self) -> None:
        self.gen.generate_cypher_file("test.cypher")

        with open("test.cypher", "r") as f:
            res = f.read()
            self.assertIsInstance(res, str)
            self.assertIn("NodeA", res)
            self.assertIn("NodeB", res)
            self.assertIn("NodeC", res)
            self.assertIn("REL_AC", res)

        try:
            os.remove("./test.cypher")
        except Exception:
            print("No cypher file data model created.")

    def test_write_constraints_file(self) -> None:
        self.gen.generate_constraints_file("test.cypher")

        with open("test.cypher", "r") as f:
            res = f.read()
            self.assertIsInstance(res, str)
            self.assertIn(
                "CREATE CONSTRAINT nodea_alpha IF NOT EXISTS FOR (n:NodeA) REQUIRE n.alpha IS UNIQUE;",
                res,
            )
            self.assertIn(
                "CREATE CONSTRAINT nodeb_beta IF NOT EXISTS FOR (n:NodeB) REQUIRE n.beta IS UNIQUE;",
                res,
            )
            self.assertIn(
                "CREATE CONSTRAINT nodec_gamma IF NOT EXISTS FOR (n:NodeC) REQUIRE n.gamma IS UNIQUE;",
                res,
            )

        try:
            os.remove("./test.cypher")
        except Exception:
            print("No constraints file data model created.")


if __name__ == "__main__":
    unittest.main()
