import unittest
import warnings

import pandas as pd
from dotenv import load_dotenv

from neo4j_runway import DataModel, Discovery, GraphDataModeler
from neo4j_runway.llm.openai import OpenAIDataModelingLLM, OpenAIDiscoveryLLM

load_dotenv()


class TestDiscoveryToDataModeler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_sequence_with_countries_data(self) -> None:
        USER_GENERATED_INPUT = {
            "general_description": "This is data on different countries.",
            "id": "unique id for a country.",
            "name": "the country name.",
            "phone_code": "country area code.",
            "capital": "the capital of the country.",
            "currency_name": "name of the country's currency.",
            "region": "primary region of the country.",
            "subregion": "subregion location of the country.",
            "timezones": "timezones contained within the country borders.",
            "latitude": "the latitude coordinate of the country center. should be part of node key.",
            "longitude": "the longitude coordinate of the country center. should be part of node key.",
        }

        # test discovery generation
        data = pd.read_csv("tests/resources/data/countries.csv")
        disc = Discovery(
            data=data, llm=OpenAIDiscoveryLLM(), user_input=USER_GENERATED_INPUT
        )

        disc.run(show_result=False)

        self.assertIsInstance(disc.discovery, str)

        # test data modeler
        with warnings.catch_warnings():  # Instructor throws DepprecationWarning only during testing... Needs fix on Instructor side
            warnings.simplefilter(action="ignore", category=DeprecationWarning)
            gdm = GraphDataModeler(
                llm=OpenAIDataModelingLLM(model_name="gpt-4o-2024-05-13"),
                discovery=disc,
            )
            gdm.create_initial_model()

        self.assertEqual(len(gdm.model_history), 1)
        self.assertIsInstance(gdm.current_model, DataModel)

    def test_sequence_with_pets_data(self) -> None:
        # test discovery generation
        data = pd.read_csv("tests/resources/data/shelters.csv")

        with self.assertWarns(UserWarning):
            disc = Discovery(data=data, llm=OpenAIDiscoveryLLM())

        disc.run(show_result=False)

        self.assertIsInstance(disc.discovery, str)
        with warnings.catch_warnings():  # Instructor throws DepprecationWarning only during testing... Needs fix on Instructor side
            warnings.simplefilter(action="ignore", category=DeprecationWarning)
            # test data modeler
            gdm = GraphDataModeler(
                llm=OpenAIDataModelingLLM(model_name="gpt-4o-2024-05-13"),
                discovery=disc,
            )

            gdm.create_initial_model()

        self.assertEqual(len(gdm.model_history), 1)
        self.assertIsInstance(gdm.current_model, DataModel)
