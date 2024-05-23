from typing import Dict, Union

from neo4j import GraphDatabase


def test_database_connection(
    credentials: Dict[str, str]
) -> Dict[str, Union[str, bool]]:
    """
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
        A dictionary containing whether the connection is valid and a message description.
            Example: {"valid": valid, "message": "Connection and Auth Verified!"}
    """
    valid = True
    try:
        d = GraphDatabase.driver(
            credentials["uri"], auth=(credentials["username"], credentials["password"])
        )
        d.verify_connectivity()
        d.verify_authentication()
    except Exception as e:
        valid = False
        return {
            "valid": valid,
            "message": f"""
                        Are your credentials correct?
                        Connection Error: {e}
                        """,
        }
    return {"valid": valid, "message": "Connection and Auth Verified!"}
