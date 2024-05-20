import unittest

from ..objects import UserInput, DataModel
from ..modeler import GraphDataModeler
from ..llm import LLM
from .resources.data_model_yaml import data_model_dict


class TestGraphDataModelerWithYaml(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        data_model = DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )
        user_input = UserInput(
            general_description="this is dummy data.",
            column_descriptions={"prop_" + str(i): "" for i in range(1, 8)},
        )
        cls.gdm = GraphDataModeler(llm=LLM(), user_input=user_input)
        cls.gdm.load_model(data_model=data_model)

    def test_generate_model_with_yaml_input(self) -> None:
        self.gdm.iterate_model(use_yaml_data_model=True)
