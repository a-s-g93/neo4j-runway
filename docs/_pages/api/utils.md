---
permalink: /api/utils/
title: test_database_connection
toc: true
toc_label: test_database_connection
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.utils import test_database_connection



Verify accurate credentials upon user submission.

    Parameters
    ----------
    credentials : Dict[str, str]

    Returns
    -------
    Dict[str, Union[str, bool]]
        A dictionary containing whether the connection is
        valid and a message description.

    Examples
    --------
    >>> credentials = {"username": "neo4j",
    ...                "password": "password",
    ...                "uri": "bolt://localhost:7687"}
    ... test_data_base_credentials(credentials=credentials)
    {"valid": valid, "message": "Connection and Auth
        Verified!"}
