from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from neo4j_runway.discovery import Discovery
from neo4j_runway.discovery.discovery import _create_discovery_prompts_for_multi_file
from neo4j_runway.utils.data import Table, TableCollection

data_dict = {
    "a.csv": {"a": "numbers", "b": "more numbers"},
    "b.csv": {"c": "many more numbers", "d": "lots of numbers"},
    "c.csv": {"e": "letters", "f": "chars"},
}
t1 = Table(
    name="a.csv",
    file_path="./a.csv",
    data=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    data_dictionary=data_dict["a.csv"],
    use_cases=["test discovery"],
)
t2 = Table(
    name="b.csv",
    file_path="./b.csv",
    data=pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
    data_dictionary=data_dict["b.csv"],
    use_cases=["test discovery"],
)
t3 = Table(
    name="c.csv",
    file_path="./c.csv",
    data=pd.DataFrame({"e": ["a", "b", "c"], "f": ["d", "e", "f"]}),
    data_dictionary=data_dict["c.csv"],
    use_cases=["test discovery"],
)
table_collection = TableCollection(
    data_directory="./",
    data_dictionary=data_dict,
    data=[t1, t2, t3],
    general_description="contain data for testing discovery",
    use_cases=["test discovery"],
)


def test_multi_file_init_table_collection() -> None:
    d = Discovery(data=table_collection)

    assert isinstance(d.data, TableCollection)
    assert d.data.size == 3


def test_create_discovery_prompts_for_multi_file_batch(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(data=table_collection, batch_size=2)

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 2
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 2


def test_create_discovery_prompts_for_multi_file_bulk(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(
        data=table_collection, bulk_process=True, num_calls=5
    )
    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 1
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 1


def test_create_discovery_prompts_for_multi_file_bulk_ignore_files(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(
        data=table_collection, bulk_process=True, num_calls=5, ignore_files=["b.csv"]
    )
    assert len(res["table_to_prompt_id"]) == 2
    assert (
        len(set(res["table_to_prompt_id"].keys()).difference({"a.csv", "c.csv"})) == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 1
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 1


def test_create_discovery_prompts_for_multi_file_custom(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(
        data=table_collection,
        custom_batches=[["a.csv", "c.csv"], ["b.csv"]],
        bulk_process=True,
    )

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 2
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 2


def test_create_discovery_prompts_for_multi_file_num_calls_same_as_file_count(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(
        data=table_collection, num_calls=3, batch_size=2
    )

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    # call count should be one less than given, there will be a final summarization call as well
    assert len(res["prompt_id_to_prompt"]) == 2
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 2


def test_create_discovery_prompts_for_multi_file_num_calls_more_than_file_count(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(data=table_collection, num_calls=10)

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 3
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 3


def test_create_discovery_prompts_for_multi_file_num_calls_less_than_file_count(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(data=table_collection, num_calls=2)

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 1
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 1


def test_create_discovery_prompts_for_multi_file_num_calls_less_than_zero(
    mock_create_discovery_prompt_multi_file: MockerFixture,
) -> None:
    res = _create_discovery_prompts_for_multi_file(data=table_collection, num_calls=-3)

    assert len(res["table_to_prompt_id"]) == 3
    assert (
        len(
            set(res["table_to_prompt_id"].keys()).difference(
                {"a.csv", "b.csv", "c.csv"}
            )
        )
        == 0
    )
    assert len(res["prompt_id_to_prompt"]) == 1
    mock_create_discovery_prompt_multi_file.assert_called()
    assert mock_create_discovery_prompt_multi_file.call_count == 1


def test_generate_data_summaries() -> None:
    d = Discovery(data=table_collection)

    d._generate_data_summaries()

    for t in d.data.data:
        assert t.discovery_content is not None


def test_run_pandas_only() -> None:
    d = Discovery(data=table_collection)

    d.run(pandas_only=True, show_result=False)

    assert d.data.discovery != ""

    for t in d.data.data:
        assert t.discovery_content is not None
        assert t.discovery_content.discovery != ""


def test_run_llm_call_custom(
    mock_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert not mock_llm.is_async

    d = Discovery(data=table_collection, llm=mock_llm)

    d.run(show_result=False, custom_batches=[["a.csv", "c.csv"], ["b.csv"]])

    assert mock_create_discovery_prompt_multi_file.call_count == 2
    assert mock_llm._get_discovery_response.call_count == 3


def test_run_llm_call_bulk(
    mock_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert not mock_llm.is_async

    d = Discovery(data=table_collection, llm=mock_llm)

    d.run(show_result=False, bulk_process=True)

    assert mock_create_discovery_prompt_multi_file.call_count == 1
    assert mock_llm._get_discovery_response.call_count == 2


def test_run_llm_call_num_calls(
    mock_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert not mock_llm.is_async

    d = Discovery(data=table_collection, llm=mock_llm)

    d.run(show_result=False, num_calls=3)

    assert mock_create_discovery_prompt_multi_file.call_count == 2
    assert mock_llm._get_discovery_response.call_count == 3


def test_run_llm_call_batch(
    mock_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert not mock_llm.is_async

    d = Discovery(data=table_collection, llm=mock_llm)

    d.run(show_result=False, batch_size=1)

    assert mock_create_discovery_prompt_multi_file.call_count == 3
    assert mock_llm._get_discovery_response.call_count == 4


def test_run_async_llm_call_custom(
    mock_async_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert mock_async_llm.is_async

    d = Discovery(data=table_collection, llm=mock_async_llm)

    d.run_async(show_result=False, custom_batches=[["a.csv", "c.csv"], ["b.csv"]])

    assert mock_create_discovery_prompt_multi_file.call_count == 2
    assert mock_async_llm._get_async_discovery_response.call_count == 3


def test_run_async_llm_call_bulk(
    mock_async_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert mock_async_llm.is_async

    d = Discovery(data=table_collection, llm=mock_async_llm)

    d.run_async(show_result=False, bulk_process=True)

    assert mock_create_discovery_prompt_multi_file.call_count == 1
    assert mock_async_llm._get_async_discovery_response.call_count == 2


def test_run_async_llm_call_num_calls(
    mock_async_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert mock_async_llm.is_async

    d = Discovery(data=table_collection, llm=mock_async_llm)

    d.run_async(show_result=False, num_calls=3)

    assert mock_create_discovery_prompt_multi_file.call_count == 2
    assert mock_async_llm._get_async_discovery_response.call_count == 3


def test_run_async_llm_call_batch(
    mock_async_llm: MagicMock, mock_create_discovery_prompt_multi_file: MockerFixture
) -> None:
    assert mock_async_llm.is_async

    d = Discovery(data=table_collection, llm=mock_async_llm)

    d.run_async(show_result=False, batch_size=1)

    assert mock_create_discovery_prompt_multi_file.call_count == 3
    assert mock_async_llm._get_async_discovery_response.call_count == 4


def test_raise_error_with_non_async_llm_and_async_run(mock_llm: MagicMock) -> None:
    assert not mock_llm.is_async

    d = Discovery(data=table_collection, llm=mock_llm)

    with pytest.raises(RuntimeError) as e:
        d.run_async(show_result=False)


def test_raise_error_with_async_llm_and_run(mock_async_llm: MagicMock) -> None:
    assert mock_async_llm.is_async

    d = Discovery(data=table_collection, llm=mock_async_llm)

    with pytest.raises(RuntimeError) as e:
        d.run(show_result=False)
