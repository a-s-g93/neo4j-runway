---
permalink: /supported-integrations/arrows-app/
---

# arrows.app

[Application](arrows.app) | [GitHub](https://github.com/neo4j-labs/arrows.app)

{% include figure popup=true image_path="/assets/images/arrows-app.png" alt="arrows.app" %}


This is a webapp that allows users to easily draw pictures of graphs. In order to integrate arrows.app with Runway, some formatting guidelines must be followed.

We need to format properties in the following way: 

```
<propertyName>: <csv_mapping> | <Python type> | <unique> or <nodekey> | <ignore>
``` 

propertyName is the is the name of the property in Neo4j.

csv_mapping is the column name the property is found under.

Sometimes there are CSV columns that refer to the same property. In this case a `Person` node has the property name. This name property is mapped to the CSV columns `name` and `knows` where `knows` identifies another `Person` that has a `KNOWS` relationship with the `Person` identified with name. We can notate this with a comma-separated list where the first column mapping is the source and the second column mapping is the target node. So in this example the Cypher would look like the following:

```cypher
(Person {name: csv.name})-[:KNOWS]->(:Person {name: csv.knows})
```

Python type is how the property is typed in Python. This will be used during ingestion to ensure that proper typing in maintained.

Identifying a property as `unique` will create a uniqueness constraint and index. 

Identifying a property as `nodekey` will create a node key constraint and index on that node including all marked properties.

If a property is not unique or a node key, then there is no need to provide the third parameter.

If a property should not be considered for data ingestion, such as a property that is created during the post ingestion phase, then it can be identified by providing `ignore` as the final parameter. 

We can identify the source CSV of a node or relationship by including a property entry like so `csv: <csv name>`. If all data is from a single CSV, then we can exclude this entry and identify the single CSV name when generating the ingestion code later on.


This will ensure that when we import into Runway, we can maintain all important attributes of our data model.

Once a data model is created, arrows.app allows the user to export as a json file. This is what will be loaded into Runway.