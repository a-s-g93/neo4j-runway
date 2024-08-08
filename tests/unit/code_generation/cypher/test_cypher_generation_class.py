from neo4j_runway import DataModel
from neo4j_runway.code_generation import StandardCypherCodeGenerator

dm = DataModel.from_arrows(
    "./tests/resources/data_models/people-pets-arrows-for-load-csv.json"
)
gen = StandardCypherCodeGenerator(data_model=dm)


def test_cypher_generation() -> None:
    assert gen.generate_cypher_string() == cypher_answer


def test_constraints_generation() -> None:
    assert gen.generate_constraints_string() == constraints_answer


cypher_answer = """WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Person {name: row.name})
SET n.age = toIntegerOrNull(row.age);
WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Address {address: row.address})
;
WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Pet {name: row.pet_name})
SET n.kind = row.pet;
WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Toy {name: row.toy})
SET n.kind = row.toy_type;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Person {name: row.name})
MATCH (target:Address {address: row.address})
MERGE (source)-[n:HAS_ADDRESS]->(target)
;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Person {name: row.name})
MATCH (target:Pet {name: row.pet_name})
MERGE (source)-[n:HAS_PET]->(target)
;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Pet {name: row.pet_name})
MATCH (target:Toy {name: row.toy})
MERGE (source)-[n:PLAYS_WITH]->(target)
;
"""

constraints_answer = """CREATE CONSTRAINT person_name IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT address_address IF NOT EXISTS FOR (n:Address) REQUIRE n.address IS UNIQUE;
CREATE CONSTRAINT pet_name IF NOT EXISTS FOR (n:Pet) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT toy_name IF NOT EXISTS FOR (n:Toy) REQUIRE n.name IS UNIQUE;
"""
