import unittest

from ..objects import DataModel


class TestGraphDataModelerWithMultiCSV(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_data_model_with_multi_csv_from_arrows(self) -> None:
        data_model = DataModel.from_arrows(
            "neo4j_runway/tests/resources/people-pets-arrows-multi-csv.json"
        )

        self.assertEqual(data_model.relationships[-1].csv_name, "shelters.csv")
        self.assertEqual(data_model.relationships[0].csv_name, "pets-arrows.csv")
        self.assertEqual(data_model.nodes[0].csv_name, "pets-arrows.csv")

    def test_data_model_with_multi_csv_from_solutions_workbench(self) -> None:
        pass
