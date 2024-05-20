import unittest

from ..objects import UserInput, DataModel
from ..modeler import GraphDataModeler
from ..llm import LLM
from .resources.data_model_yaml import data_model_dict


class LLMMock:
    def get_data_model_response(*args, **kargs) -> DataModel:
        return DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )
    
class TestGraphDataModelerFree(unittest.TestCase):

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
        cls.gdm = GraphDataModeler(llm=LLMMock, user_input=user_input)

    def test_load_model(self) -> None:

        self.gdm.load_model(data_model=self.data_model)
        self.assertEqual(self.gdm.current_model, self.data_model)

    def test_iterate_model(self) -> None:
        self.gdm.model_history = []
        self.gdm.create_initial_model()
        self.gdm.iterate_model(2)

        self.assertEqual(len(self.gdm.model_history), 3)