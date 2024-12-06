from unittest.mock import MagicMock

import pandas as pd
import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.utils.data import Table, TableCollection
from neo4j_runway.warnings import ExperimentalFeatureWarning


def test_single_table_run(table_1: Table, mock_llm_async: MagicMock) -> None:
    d = Discovery(data=table_1, llm=mock_llm_async)

    d.run_async(show_result=False)

    assert d.data.discovery is not None
    assert d.data.tables[0].discovery_content is not None
    assert d.data.tables[0].discovery is not None


def test_multi_file_run(
    table_collection: TableCollection, mock_llm_async: MagicMock
) -> None:
    with pytest.warns(ExperimentalFeatureWarning):
        d = Discovery(data=table_collection, llm=mock_llm_async)

    d.run_async(show_result=False)

    assert d.data.discovery is not None
    for t in d.data.tables:
        assert t.discovery_content is not None
        assert t.discovery is not None
