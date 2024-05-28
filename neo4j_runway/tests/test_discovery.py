import unittest

import pandas as pd

from ..discovery.discovery import Discovery
from ..llm.llm import LLM
from ..objects import UserInput

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

    def test_initialized_variables(self) -> None:
        """
        Ensure that all initial variables are set accurately.
        """

        self.assertEqual(self.disc.discovery, "")
        self.assertEqual(
            set(self.disc.columns_of_interest), {"id", "feature_1", "feature_2"}
        )
        self.assertEqual(set(self.disc.data.columns), {"id", "feature_1", "feature_2"})

    def test_init_with_UserInput(self) -> None:
        user_input = UserInput(
            general_description="This is a general description.",
            column_descriptions={"feature_1": "column one", "feature_2": " column two"},
        )

        self.test_disc = Discovery(
            llm=LLM(), user_input=user_input, data=pd.DataFrame(data)
        )

        self.assertEqual(self.test_disc.discovery, "")
        self.assertEqual(
            set(self.test_disc.columns_of_interest), {"feature_1", "feature_2"}
        )
        self.assertEqual(set(self.test_disc.data.columns), {"feature_1", "feature_2"})

    def test_init_with_no_desired_columns(self) -> None:
        d = Discovery(llm=LLM(), data=pd.DataFrame(data))

        self.assertEqual({"id", "feature_1", "feature_2", "bad_feature"}, set(d.columns_of_interest))

        with self.assertWarns(Warning):
            Discovery(llm=LLM(), data=pd.DataFrame(data))
    
    def test_pandas_only(self) -> None:
        d = Discovery(data=pd.DataFrame(data))
        d.run()

        self.assertEqual(d.discovery, "")
        self.assertIsNotNone(d.df_info)
        self.assertIsNotNone(d.numeric_data_description)
        self.assertIsNotNone(d.categorical_data_description)

if __name__ == "__main__":
    unittest.main()
