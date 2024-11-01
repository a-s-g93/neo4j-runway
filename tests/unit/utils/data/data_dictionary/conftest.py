from typing import Any, Dict

import pytest


@pytest.fixture(scope="function")
def validation_info_context() -> Dict[str, Any]:
    return {"column_names": ["col_a", "col_b", "col_c", "col_d", "col_a_alias"]}
