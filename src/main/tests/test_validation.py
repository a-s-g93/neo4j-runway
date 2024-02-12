import unittest
import os

from summarizer.summarizer import Summarizer
from llm.llm import LLM
from tests.dummies import test_model_valid, test_model_invalid, test_columns, test_user_data, test_data


class TestValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.summarizer = Summarizer(llm=LLM(), user_input=test_user_data, data=test_data)
    
    def test_property_validation(self):
        """
        Test property existance in csv column names validation.
        """

        self.assertTrue(self.summarizer._validate_properties_exist_in_csv(data_model=test_model_valid)['valid'])
        self.assertFalse(self.summarizer._validate_properties_exist_in_csv(data_model=test_model_invalid)['valid'])




if __name__ == '__main__':
    unittest.main()