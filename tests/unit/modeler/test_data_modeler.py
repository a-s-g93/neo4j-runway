import unittest

from graphviz import Digraph

from neo4j_runway.inputs import UserInput
from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.models import DataModel
from tests.resources.answers.data_model_yaml import data_model_dict


class LLMMock:
    def _get_data_model_response(*args, **kargs) -> DataModel:
        return DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )

    def _get_initial_data_model_response(*args, **kargs) -> DataModel:
        return DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )


class DiscoveryMock:
    discovery = "Fake Discovery"


USER_GENERATED_INPUT = {
    "general_description": "This is data on some interesting data.",
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}

USER_GENERATED_INPUT_BAD = {
    # 'general_description': 'This is data on some interesting data.',
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}


class TestGraphDataModeler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_model = DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )

        user_input = UserInput(
            general_description="this is dummy data.",
            column_descriptions={"prop_" + str(i): "" for i in range(1, 8)},
        )

        cls.gdm = GraphDataModeler(
            llm=LLMMock(), user_input=user_input, discovery=DiscoveryMock()
        )

    def test_load_model(self) -> None:
        self.gdm.load_model(data_model=self.data_model)
        self.assertEqual(self.gdm.current_model, self.data_model)

    def test_iterate_model(self) -> None:
        self.gdm.model_history = []
        self.gdm.create_initial_model()
        self.gdm.iterate_model(2)

        self.assertEqual(len(self.gdm.model_history), 3)

    def test_get_model(self) -> None:
        """
        Test get model logic.
        """
        self.gdm.model_history = [self.data_model, "data model", self.data_model]
        self.assertEqual(self.gdm.get_model(version=2, as_dict=False), "data model")
        self.assertEqual(
            self.gdm.get_model(version=1, as_dict=True), self.data_model.model_dump()
        )
        self.assertEqual(self.gdm.get_model(version=-3, as_dict=False), self.data_model)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=4, as_dict=False)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=0, as_dict=False)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=-4, as_dict=True)

    def test_current_model_viz(self) -> None:
        """
        Test viz returns Digraph.
        """
        self.gdm.model_history = [self.data_model]
        self.assertIsInstance(self.gdm.current_model_viz, Digraph)

    def test_discovery_warning(self) -> None:
        """
        Test warning is triggered if no discovery passed to constructor.
        """

        with self.assertWarns(Warning):
            GraphDataModeler(
                llm="llm",
                user_input=USER_GENERATED_INPUT,
                # discovery="discovery",
                general_data_description="desc",
                categorical_data_description="desc",
                numeric_data_description="desc",
                feature_descriptions="desc",
            )

    def test_no_general_info_in_user_input(self) -> None:
        """
        Test error if no general description of data is present in user info.
        """

        with self.assertWarns(Warning):
            gdm = GraphDataModeler(
                llm="llm",
                user_input=USER_GENERATED_INPUT_BAD,
                discovery="discovery",
                general_data_description="desc",
                categorical_data_description="desc",
                numeric_data_description="desc",
                feature_descriptions="desc",
            )

    def test_no_discovery_no_user_input_with_allowed_columns(self) -> None:
        with self.assertWarns(Warning):
            gdm = GraphDataModeler(
                llm="llm",
                discovery="discovery",
                general_data_description="desc",
                categorical_data_description="desc",
                numeric_data_description="desc",
                feature_descriptions="desc",
                allowed_columns=["feature_1", "feature_2", "id"],
            )

            self.assertEqual(["feature_1", "feature_2", "id"], gdm.columns_of_interest)


if __name__ == "__main__":
    unittest.main()
