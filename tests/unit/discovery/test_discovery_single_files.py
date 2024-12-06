import sys
import unittest
from io import StringIO

import pandas as pd

from neo4j_runway.discovery import Discovery
from neo4j_runway.utils.data import Table, TableCollection
from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema

table_name = "test.csv"
general_description = "This is data on some interesting data."
table_schema = TableSchema(
    name=table_name,
    columns=[
        Column(name="id", description="unique id for a node."),
        Column(name="feature_1", description="this a feature"),
        Column(name="feature_2", description="this is also a feature"),
    ],
)

data = {
    "id": [1, 2, 3, 4, 5],
    "feature_1": ["a", "b", "c", "d", "e"],
    "feature_2": ["z", "y", "x", "w", "v"],
    "bad_feature": [11, 22, 33, 44, 55],
}

table = Table(
    name=table_name,
    file_path="./test.csv",
    dataframe=pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "feature_1": ["a", "b", "c", "d", "e"],
            "feature_2": ["z", "y", "x", "w", "v"],
        }
    ),
    general_description=general_description,
    table_schema=table_schema,
    use_cases=["What do?"],
)


class LLMMock:
    pass


class TestDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.disc = Discovery(
            llm=LLMMock(),
            data=pd.DataFrame(data),
            data_dictionary=DataDictionary(table_schemas=[table_schema]),
        )

    def test_initialized_variables(self) -> None:
        """
        Ensure that all initial variables are set accurately.
        """

        self.assertIsNone(self.disc.data.discovery)
        self.assertEqual(
            set(self.disc.data.tables[0].column_names),
            {"id", "feature_1", "feature_2"},
        )

    def test_init_with_no_desired_columns_dataframe(self) -> None:
        d = Discovery(llm=LLMMock(), data=pd.DataFrame(data))

        self.assertEqual(
            {"id", "feature_1", "feature_2", "bad_feature"},
            set(d.data.tables[0].dataframe.columns),
        )

    def test_view_discovery_no_notebook(self) -> None:
        d = Discovery(data=pd.DataFrame(data))
        test_disc = "TEST\ntest"
        d.data.discovery = test_disc

        self.assertIsNotNone(d.discovery)

        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        d.view_discovery(notebook=False)
        sys.stdout = sys.__stdout__
        self.assertEqual(capturedOutput.getvalue(), test_disc + "\n")

    def test_view_discovery_with_notebook(self) -> None:
        d = Discovery(data=pd.DataFrame(data))
        test_disc = "TEST\ntest"
        d.data.discovery = test_disc

        self.assertIsNotNone(d.discovery)

        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        d.view_discovery(notebook=True)
        sys.stdout = sys.__stdout__
        self.assertEqual(
            capturedOutput.getvalue().strip(),
            "<IPython.core.display.Markdown object>",
        )

    def test_pandas_only_single_file_dataframe(self) -> None:
        d = Discovery(data=pd.DataFrame(data))
        d.run()

        self.assertNotEqual(d.data.discovery, "")
        self.assertIsNotNone(d.discovery)

    def test_init_with_table(self) -> None:
        d = Discovery(llm=LLMMock(), data=table)

        self.assertIsInstance(d.data, TableCollection)
        self.assertEqual(
            set(d.data.get_table(table_name).column_names),
            set(table.table_schema.column_names),
        )
        self.assertEqual(
            set(d.data.tables[0].table_schema.column_names),
            set(table.table_schema.column_names),
        )
        self.assertEqual(d.data.size, 1)
        self.assertEqual(len(d.data.tables[0].dataframe), 5)
        self.assertEqual(d.data.use_cases[0], "What do?")

    def test_init_with_no_desired_columns_table(self) -> None:
        d = Discovery(llm=LLMMock(), data=table)

        self.assertEqual(
            {"id", "feature_1", "feature_2"},
            set(d.data.tables[0].dataframe.columns),
        )


if __name__ == "__main__":
    unittest.main()
