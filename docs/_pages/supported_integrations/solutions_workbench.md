---
permalink: /supported-integrations/solutions-workbench/
title: "Solutions Workbench"
---

[Documentation](https://help.neo4j.solutions/neo4j-solutions/cypher-workbench/) | [GitHub](https://github.com/neo4j-labs/cypher-workbench)

{% include figure popup=true image_path="/assets/images/cypher_workbench_blog_modeling_screenshot.png" alt="Solutions Workbench" %}

Solutions Workbench (Also known as Cypher Workbench) provides a suite of tools to build a Neo4j project. 
Runway integrates with it's data modeling service to import a data model in json format and generate ingestion code. 

In order to integrate with Runway, some formatting guidelines must be followed.

Each node and relationship has a `description` field. If multiple CSVs are to be ingested, this field must contain the csv name.

Each property has a `Reference Data` field. This field must contain the CSV column the property is found under.

Each property also has four parameters for `Node Key`, `Unique`, `Indexed` and `Must Exist`. Currently (v0.5.2) Runway only tracks `Node Key` and `Unique`. Indexing and existance is assumed based on these first two parameters. In future releases, this will be addressed. 