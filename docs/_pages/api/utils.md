---
permalink: /api/utils/
---
# test_database_connection

Verify accurate credentials upon user submission.

    Parameters
    ----------
    credentials : Dict[str, str]
    The Neo4j credentials. Must be the following format:
        {"username": "neo4j",
        "password": "password",
        "uri": "bolt://localhost:7687"}

    Returns
    -------
    Dict[str, Union[str, bool]]
    A dictionary containing whether the connection is valid
        and a message description.
        Example: {"valid": valid, "message": "Connection and
        Auth Verified!"}
