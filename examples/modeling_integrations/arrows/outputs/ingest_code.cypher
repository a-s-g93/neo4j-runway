WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Person {name: row.name})
SET n.age = toIntegerOrNull(row.age);
WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:Address {city: row.city, street: row.street})
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
UNWIND rows AS row
MERGE (n:Shelter {name: row.shelter_name})
;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Person {name: row.name})
MATCH (target:Address {city: row.city, street: row.street})
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
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Pet {name: row.pet_name})
MATCH (target:Shelter {name: row.shelter_name})
MERGE (source)-[n:FROM_SHELTER]->(target)
;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Shelter {name: row.shelter_name})
MATCH (target:Address {city: row.city, street: row.street})
MERGE (source)-[n:HAS_ADDRESS]->(target)
;
WITH $dict.rows AS rows
UNWIND rows as row
MATCH (source:Person {name: row.name})
MATCH (target:Person {name: row.knows})
MERGE (source)-[n:KNOWS]->(target)
;
