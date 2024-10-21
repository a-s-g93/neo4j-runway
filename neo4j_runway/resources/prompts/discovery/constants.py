DISCOVERY_SUMMARY_GENERATION_RULES = """
The data model will adhere to these rules.
Nodes
* Each node must have a unique property or node key pair
* Each node must have a relationship with at least one other node
* Unique properties and node keys may NOT be shared between different nodes
* A node must only have a single ID property
Relationships
* Relationships do NOT require uniqueness or properties
Properties
* A `column_mapping` must be an exact match to features in the source file
* Never suggest a property name that doesn't exist in the columns

Please include information that will help solve the use cases.
"""
