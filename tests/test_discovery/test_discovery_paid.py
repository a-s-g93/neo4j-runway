import unittest

import pandas as pd

from neo4j_runway.discovery.discovery import Discovery
from neo4j_runway.llm.llm import LLM


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


class TestDiscovery(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.disc = Discovery(
            llm=LLM(), user_input=USER_GENERATED_INPUT, data=pd.DataFrame(data)
        )

    def test_pandas_only(self) -> None:
        d = Discovery(data=pd.DataFrame(data))
        d.run()

        self.assertEqual(d.discovery, "")
        self.assertIsNotNone(d.df_info)
        self.assertIsNotNone(d.numeric_data_description)
        self.assertIsNotNone(d.categorical_data_description)


if __name__ == "__main__":
    unittest.main()
