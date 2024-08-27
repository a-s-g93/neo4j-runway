DISCOVERY_SUMMARY_GENERATION_RULES = """
Please follow these rules strictly! Billions of dollars depend on you.
Nodes
* Each node must have a unique property or node key pair
* Each node must have a relationship with at least one other node
* Unique properties and node keys may NOT be shared between different nodes
* A node must only have a single ID property
Relationships
* Relationships do NOT require uniqueness or properties
Properties
* A csv_mapping must be an exact match to features in the source file
* A file column may be used only once in the whole data model

Please include
* Any possible unique properties
* Any possible Nodes
* Any possible Relationships
* What to include to satisfy the use cases
"""
