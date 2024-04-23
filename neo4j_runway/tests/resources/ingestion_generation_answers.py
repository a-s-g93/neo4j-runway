constraints_key_a_1 = "nodea_uniqueprop1"
constraints_key_a_3 = "nodea_uniqueprop3"
constraints_key_b = "nodeb_uniqueprop2"
constraint_a_1 = f"CREATE CONSTRAINT {constraints_key_a_1} IF NOT EXISTS FOR (n:NodeA) REQUIRE n.uniqueProp1 IS UNIQUE;\n"
constraint_a_3 = f"CREATE CONSTRAINT {constraints_key_a_3} IF NOT EXISTS FOR (n:NodeA) REQUIRE n.uniqueProp3 IS UNIQUE;\n"
constraint_b = f"CREATE CONSTRAINT {constraints_key_b} IF NOT EXISTS FOR (n:NodeB) REQUIRE n.uniqueProp2 IS UNIQUE;\n"
set_unique_property_a = "uniqueProp1: row.unique_prop_1, uniqueProp3: row.unique_prop_3"
set_unique_property_b = "uniqueProp2: row.unique_prop_2"
set_properties_a = "SET n.prop1 = row.prop_1"
set_properties_b = "SET n.prop2 = row.prop_2, n.prop3 = row.prop_3"
set_properties_rel_1 = "SET n.relProp = row.rel_prop"
match_node_a = "MATCH (n:NodeA" + "{" + f"{set_unique_property_a}" + "})"
match_node_b = "MATCH (n:NodeB" + "{" + f"{set_unique_property_b}" + "})"
merge_node_standard_a = (
    "WITH $dict.rows AS rows\nUNWIND rows AS row\nMERGE (n:NodeA {"
    + set_unique_property_a
    + "})\n"
    + set_properties_a
)
merge_node_load_csv_b = (
    "LOAD CSV WITH HEADERS FROM 'file:///file_name' as row\nCALL {\n\tWITH row\n\tMERGE (n:NodeB {"
    + set_unique_property_b
    + "})\n"
    + set_properties_b
    + "} IN TRANSACTIONS OF 10000 ROWS;\n"
)
merge_relationship_standard = (
    "WITH $dict.rows AS rows\nUNWIND rows as row\n"
    + "\tMATCH (source:NodeA)\n"
    + "\tMATCH (target:NodeB)\n"
    + "\tMERGE (source)-[n:HAS_RELATIONSHIP]->(target)\n"
    + f"\t{set_properties_rel_1}"
)
merge_relationship_load_csv = (
    "LOAD CSV WITH HEADERS FROM 'file:///file_name' as row\n"
    + "\tMATCH (source:NodeA)\n"
    + "\tMATCH (target:NodeB)\n"
    + "\tMERGE (source)-[n:HAS_RELATIONSHIP]->(target)\n"
    + f"\t{set_properties_rel_1}"
    + "} IN TRANSACTIONS OF 50 ROWS;"
)
