import pandas as pd

from neo4j_runway.discovery.discovery_content import DiscoveryContent


def test_init() -> None:
    DiscoveryContent(
        pandas_general_description="general",
        pandas_categorical_description=pd.DataFrame(),
        pandas_numerical_description=pd.DataFrame(),
        discovery="test discovery",
    )


def test_str_dunder() -> None:
    ds = DiscoveryContent(
        pandas_general_description="general",
        pandas_categorical_description=pd.DataFrame(),
        pandas_numerical_description=pd.DataFrame(),
        discovery="test discovery",
    )

    assert "Data General Info" in ds.__str__()
    assert "Numeric Data Descriptions" in ds.__str__()
    assert "Categorical Data Descriptions" in ds.__str__()
    assert "LLM Generated Discovery" in ds.__str__()
    assert "test discovery" in ds.__str__()
    assert "general" in ds.__str__()
