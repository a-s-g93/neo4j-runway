import warnings
from unittest.mock import MagicMock

from neo4j_runway.inputs import UserInput
from neo4j_runway.llm.openai import OpenAIDataModelingLLM
from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.models import DataModel
from tests.resources.answers.data_model_yaml import data_model_dict


def test_generate_model_with_yaml_input(
    graph_data_modeler_with_data_model: MagicMock,
) -> None:
    graph_data_modeler_with_data_model.iterate_model(use_yaml_data_model=True)
    assert len(graph_data_modeler_with_data_model.model_history) == 2
