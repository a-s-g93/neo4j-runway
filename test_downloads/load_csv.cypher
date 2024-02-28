CREATE CONSTRAINT battle_name IF NOT EXISTS FOR (n:Battle) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT king_name IF NOT EXISTS FOR (n:King) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT force_name IF NOT EXISTS FOR (n:Force) REQUIRE n.name IS UNIQUE;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Battle {name: row.name})
SET n.battle_number = row.battle_number, n.location = row.location, n.year = row.year, n.region = row.region, n.major_death = row.major_death, n.note = row.note, n.attacker_commander = row.attacker_commander, n.defender_commander = row.defender_commander, n.summer = row.summer, n.battle_type = row.battle_type, n.defender_king = row.defender_king, n.attacker_outcome = row.attacker_outcome, n.major_capture = row.major_capture, n.defender_size = row.defender_size, n.attacker_king = row.attacker_king, n.attacker_size = row.attacker_size} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:King {name: row.name})
} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Force {name: row.name})
} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Battle{name: row.name})
	MATCH (target:Force{name: row.name})
	MERGE (source)-[:DEFENDED_BY]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Battle{name: row.name})
	MATCH (target:King{name: row.name})
	MERGE (source)-[:INVOLVED_IN]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
