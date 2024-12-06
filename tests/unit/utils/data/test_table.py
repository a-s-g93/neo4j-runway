import pandas as pd

from neo4j_runway.utils.data import Table


def test_init() -> None:
    t = Table(
        name="test.csv",
        file_path="./test.csv",
        dataframe=pd.DataFrame(),
        general_description="general",
        table_schema={"col_a": "this is a column."},
        use_cases=["A use case."],
    )

    assert t.name == "test.csv"
    assert t.file_path == "./test.csv"
    assert isinstance(t.dataframe, pd.DataFrame)
    assert t.general_description == "general"
    assert "col_a" in t.table_schema.column_names
    assert "A use case." in t.use_cases
    assert t.discovery_content is None
    assert t.discovery == ""
