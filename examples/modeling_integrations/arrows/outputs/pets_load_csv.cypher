CREATE CONSTRAINT person_name IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT address_city_street IF NOT EXISTS FOR (n:Address) REQUIRE (n.city, n.street) IS NODE KEY;
CREATE CONSTRAINT pet_name IF NOT EXISTS FOR (n:Pet) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT toy_name IF NOT EXISTS FOR (n:Toy) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT shelter_name IF NOT EXISTS FOR (n:Shelter) REQUIRE n.name IS UNIQUE;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MERGE (n:Person {name: row.name})
    SET n.age = toIntegerOrNull(row.age)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MERGE (n:Address {city: row.city, street: row.street})
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MERGE (n:Pet {name: row.pet_name})
    SET n.kind = row.pet
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MERGE (n:Toy {name: row.toy})
    SET n.kind = row.toy_type
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./shelters-2.csv' as row
CALL {
    WITH row
    MERGE (n:Shelter {name: row.shelter_name})
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MATCH (source:Person {name: row.name})
    MATCH (target:Address {city: row.city, street: row.street})
    MERGE (source)-[n:HAS_ADDRESS]->(target)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MATCH (source:Person {name: row.name})
    MATCH (target:Pet {name: row.pet_name})
    MERGE (source)-[n:HAS_PET]->(target)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MATCH (source:Pet {name: row.pet_name})
    MATCH (target:Toy {name: row.toy})
    MERGE (source)-[n:PLAYS_WITH]->(target)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./shelters-2.csv' as row
CALL {
    WITH row
    MATCH (source:Pet {name: row.pet_name})
    MATCH (target:Shelter {name: row.shelter_name})
    MERGE (source)-[n:FROM_SHELTER]->(target)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./shelters-2.csv' as row
CALL {
    WITH row
    MATCH (source:Shelter {name: row.shelter_name})
    MATCH (target:Address {city: row.city, street: row.street})
    MERGE (source)-[n:HAS_ADDRESS]->(target)
} IN TRANSACTIONS OF 100 ROWS;
:auto LOAD CSV WITH HEADERS FROM 'file:///./pets-2.csv' as row
CALL {
    WITH row
    MATCH (source:Person {name: row.name})
    MATCH (target:Person {name: row.knows})
    MERGE (source)-[n:KNOWS]->(target)
} IN TRANSACTIONS OF 100 ROWS;
