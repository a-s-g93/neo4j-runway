import pandas as pd
import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.utils.data import Table, TableCollection
from neo4j_runway.warnings import ExperimentalFeatureWarning


def test_single_dataframe_run_pandas_only() -> None:
    d = Discovery(data=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))

    d.run(pandas_only=True)

    assert d.data.discovery is not None
    assert d.data.tables[0].discovery_content is not None
    assert d.data.tables[0].discovery is not None


def test_single_table_run_pandas_only(table_1: Table) -> None:
    d = Discovery(data=table_1)

    d.run(pandas_only=True)

    assert d.data.discovery is not None
    assert d.data.tables[0].discovery_content is not None
    assert d.data.tables[0].discovery is not None


def test_multi_file_run_pandas_only(table_collection: TableCollection) -> None:
    with pytest.warns(ExperimentalFeatureWarning):
        d = Discovery(data=table_collection)

    d.run(pandas_only=True)

    assert d.data.discovery is not None
    for t in d.data.tables:
        assert t.discovery_content is not None
        assert t.discovery is not None
