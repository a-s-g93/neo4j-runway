import unittest

from neo4j_runway.objects import UserInput

USER_GENERATED_INPUT = {
    "general_description": "This is data on some interesting data.",
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}

data = {
    "id": [1, 2, 3, 4, 5],
    "feature_1": ["a", "b", "c", "d", "e"],
    "feature_2": ["z", "y", "x", "w", "v"],
    "bad_feature": [11, 22, 33, 44, 55],
}


class TestUserInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_no_general_description(self) -> None:
        UserInput(column_descriptions={"feature_1": "f1", "feature_2": "f2"})

    def test_bad_col_description(self) -> None:
        with self.assertRaises(ValueError):
            UserInput(
                general_description="gen",
                column_descriptions={"feature_1": 1, "feature_2": "f2"},
            )

    def test_empty_col_description(self) -> None:
        with self.assertWarns(Warning):
            UserInput(general_description="gen", column_descriptions={})


if __name__ == "__main__":
    unittest.main()
