import sys
import unittest
from io import StringIO

import pandas as pd

from neo4j_runway.discovery import Discovery
from neo4j_runway.discovery.discovery_content import DiscoveryContent
from neo4j_runway.inputs import UserInput
from neo4j_runway.utils.data import Table, TableCollection

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

table = Table(
    name="test.csv",
    file_path="./test.csv",
    data=pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "feature_1": ["a", "b", "c", "d", "e"],
            "feature_2": ["z", "y", "x", "w", "v"],
        }
    ),
    general_description=USER_GENERATED_INPUT["general_description"],
    data_dictionary={
        "id": "unique id for a node.",
        "feature_1": "this is a feature",
        "feature_2": "this is also a feature",
    },
    use_cases=["What do?"],
)


class LLMMock:
    pass


class TestDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.disc = Discovery(
            llm=LLMMock(),
            user_input=USER_GENERATED_INPUT,
            data=pd.DataFrame(data),
        )

    def test_initialized_variables(self) -> None:
        """
        Ensure that all initial variables are set accurately.
        """

        self.assertEqual(self.disc.discovery, "")
        self.assertEqual(
            set(self.disc.data.data[0].data.columns), {"id", "feature_1", "feature_2"}
        )

    def test_init_with_UserInput_dataframe(self) -> None:
        user_input = UserInput(
            general_description="This is a general description.",
            column_descriptions={"feature_1": "column one", "feature_2": " column two"},
        )

        self.test_disc = Discovery(
            llm=LLMMock(), user_input=user_input, data=pd.DataFrame(data)
        )

        self.assertIsInstance(self.test_disc.data, TableCollection)
        self.assertEqual(self.test_disc.discovery, "")
        self.assertEqual(
            set(self.test_disc.data.data[0].data.columns), {"feature_1", "feature_2"}
        )

    def test_init_with_no_desired_columns_dataframe(self) -> None:
        with self.assertWarns(Warning):
            d = Discovery(llm=LLMMock(), data=pd.DataFrame(data))

            self.assertEqual(
                {"id", "feature_1", "feature_2", "bad_feature"},
                set(d.data.data[0].data.columns),
            )

    def test_view_discovery_no_notebook(self) -> None:
        with self.assertWarns(Warning):
            d = Discovery(data=pd.DataFrame(data))
            test_disc = "TEST\ntest"
            d.data.discovery_content = DiscoveryContent(
                discovery=test_disc,
                pandas_general_description="",
                pandas_numerical_description=pd.DataFrame(),
                pandas_categorical_description=pd.DataFrame(),
            )

            capturedOutput = StringIO()
            sys.stdout = capturedOutput
            d.view_discovery(notebook=False)
            sys.stdout = sys.__stdout__
            self.assertEqual(capturedOutput.getvalue(), test_disc + "\n")

    def test_view_discovery_with_notebook(self) -> None:
        with self.assertWarns(Warning):
            d = Discovery(data=pd.DataFrame(data))
            test_disc = "TEST\ntest"
            d.data.discovery_content = DiscoveryContent(
                discovery=test_disc,
                pandas_general_description="",
                pandas_numerical_description=pd.DataFrame(),
                pandas_categorical_description=pd.DataFrame(),
            )

            capturedOutput = StringIO()
            sys.stdout = capturedOutput
            d.view_discovery(notebook=True)
            sys.stdout = sys.__stdout__
            self.assertEqual(
                capturedOutput.getvalue().strip(),
                "<IPython.core.display.Markdown object>",
            )

    def test_pandas_only_single_file_dataframe(self) -> None:
        with self.assertWarns(Warning):
            d = Discovery(data=pd.DataFrame(data))
            d.run()

            self.assertNotEqual(d.data.discovery, "")

    def test_init_with_table(self) -> None:
        d = Discovery(llm=LLMMock(), data=table)

        self.assertIsInstance(d.data, TableCollection)
        self.assertEqual(
            set(d.data.data_dictionary.keys()), set(table.data_dictionary.keys())
        )
        self.assertEqual(
            set(d.data.data[0].data_dictionary.keys()),
            set(table.data_dictionary.keys()),
        )
        self.assertEqual(d.data.size, 1)
        self.assertEqual(len(d.data.data[0].data), 5)
        self.assertEqual(d.data.use_cases[0], "What do?")

    def test_init_with_no_desired_columns_table(self) -> None:
        d = Discovery(llm=LLMMock(), data=table)

        self.assertEqual(
            {"id", "feature_1", "feature_2"},
            set(d.data.data[0].data.columns),
        )


if __name__ == "__main__":
    unittest.main()
