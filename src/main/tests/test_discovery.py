import unittest

import pandas as pd

from objects.node import Node
from objects.relationship import Relationship
from objects.property import Property
from objects.data_model import DataModel
from modeler.modeler import GraphDataModeler
from discovery.discovery import Discovery
from llm.llm import LLM

USER_GENERATED_INPUT = {
    'General Description': 'This is data on some interesting data.',
    'id': 'unique id for a node.',
    'feature_1': "this is a feature",
    "feature_2": "this is also a feature"
}

data = {'id': [1,2,3,4,5], 
         'feature_1': ['a', 'b', 'c', 'd', 'e'],
         'feature_2': ['z', 'y', 'x', 'w', 'v'],
         'bad_feature': [11, 22, 33, 44, 55]
         }

class TestDiscovery(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.disc = Discovery(llm=LLM(), user_input=USER_GENERATED_INPUT, data=pd.DataFrame(data))

    def test_initialized_variables(self) -> None:
        """
        Ensure that all initial variables are set accurately.
        """

        self.assertEqual(self.disc.discovery, "")
        self.assertEqual(set(self.disc.columns_of_interest), {"id", "feature_1", "feature_2"})
        self.assertEqual(set(self.disc.data.columns), {"id", "feature_1", "feature_2"})
        
if __name__ == "__main__":
    unittest.main()
