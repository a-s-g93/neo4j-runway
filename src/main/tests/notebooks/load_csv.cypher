CREATE CONSTRAINT person_name IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT address_name IF NOT EXISTS FOR (n:Address) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT pet_name IF NOT EXISTS FOR (n:Pet) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT toy_name IF NOT EXISTS FOR (n:Toy) REQUIRE n.name IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Person {name: row.name})
SET n.age = row.age} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Address {name: row.name})
SET n.street = row.street, n.city = row.city} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Pet {name: row.name})
SET n.kind = row.kind, n.name = row.name} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Toy {name: row.name})
SET n.kind = row.kind} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Person{name: row.name})
	MATCH (target:Address{name: row.name})
	MERGE (source)-[:HAS_ADDRESS]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Person{name: row.name})
	MATCH (target:Person{name: row.name})
	MERGE (source)-[:KNOWS]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Person{name: row.name})
	MATCH (target:Pet{name: row.name})
	MERGE (source)-[:HAS_PET]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Pet{name: row.name})
	MATCH (target:Toy{name: row.name})
	MERGE (source)-[:PLAYS_WITH]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

