from neo4j_runway import DataModel
from neo4j_runway.code_generation import LoadCSVCodeGenerator


def test_generation() -> None:
    dm = DataModel.from_arrows(
        "./tests/resources/data_models/people-pets-arrows-for-load-csv.json"
    )
    gen = LoadCSVCodeGenerator(data_model=dm)
    assert gen.generate_load_csv_cypher_string() == load_csv_code_answer


load_csv_code_answer = """CREATE CONSTRAINT person_name IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT address_address IF NOT EXISTS FOR (n:Address) REQUIRE n.address IS UNIQUE;
CREATE CONSTRAINT pet_name IF NOT EXISTS FOR (n:Pet) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT toy_name IF NOT EXISTS FOR (n:Toy) REQUIRE n.name IS UNIQUE;
LOAD CSV WITH HEADERS FROM 'file:///./pets-arrows.csv' as row
CALL {
    WITH row
    MERGE (n:Person {name: row.name})
    SET n.age = toIntegerOrNull(row.age)
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./pets-arrows.csv' as row
CALL {
    WITH row
    MERGE (n:Address {address: row.address})
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./pets-arrows.csv' as row
CALL {
    WITH row
    MERGE (n:Pet {name: row.pet_name})
    SET n.kind = row.pet
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./pets-arrows.csv' as row
CALL {
    WITH row
    MERGE (n:Toy {name: row.toy})
    SET n.kind = row.toy_type
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./' as row
CALL {
    WITH row
    MATCH (source:Person {name: row.name})
    MATCH (target:Address {address: row.address})
    MERGE (source)-[n:HAS_ADDRESS]->(target)
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./' as row
CALL {
    WITH row
    MATCH (source:Person {name: row.name})
    MATCH (target:Pet {name: row.pet_name})
    MERGE (source)-[n:HAS_PET]->(target)
} IN TRANSACTIONS OF 100 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///./' as row
CALL {
    WITH row
    MATCH (source:Pet {name: row.pet_name})
    MATCH (target:Toy {name: row.toy})
    MERGE (source)-[n:PLAYS_WITH]->(target)
} IN TRANSACTIONS OF 100 ROWS;
"""
