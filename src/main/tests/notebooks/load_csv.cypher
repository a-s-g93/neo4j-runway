CREATE CONSTRAINT person_name IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT toy_name IF NOT EXISTS FOR (n:Toy) REQUIRE n.name IS UNIQUE;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Person {name: row.name})
SET n.age = row.age} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Address {})
SET n.street = row.street, n.city = row.city} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Pet {})
SET n.name = row.pet_name, n.kind = row.pet} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Toy {name: row.toy})
SET n.kind = row.toy_type} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Person{name: row.name})
	MATCH (target:Address{})
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
	MATCH (target:Pet{})
	MERGE (source)-[:HAS_PET]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Pet{})
	MATCH (target:Toy{name: row.toy})
	MERGE (source)-[:PLAYS_WITH]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
