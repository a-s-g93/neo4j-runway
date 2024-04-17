from typing import Dict, Union

from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, AuthError


def test_database_connection(
    credentials: Dict[str, str]
) -> Dict[str, Union[str, bool]]:
    """
    Verify accurate credentials upon user submission.
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
                        Are your credentials correct?\n
                        Connection Error: {e}
                        """,
        }
    return {"valid": valid, "message": "Connection and Auth Verified!"}
