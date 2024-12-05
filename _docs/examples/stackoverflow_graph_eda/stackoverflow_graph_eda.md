---
permalink: /examples/stackoverflow-graph-eda/
title: Stackoverflow Exploratory Data Analysis
toc: true
toc_label:
toc_icon: "fa-solid fa-plane"
---
This notebooks demonstrates how to use Runway's EDA module with Neo4j's example dataset containing information on Stackoverflow.


```python
import os

from neo4j_runway.database.neo4j import Neo4jGraph
from neo4j_runway.graph_eda import GraphEDA
```

## Create a Neo4j Instance


```python
g = Neo4jGraph(uri=os.environ.get("NEO4J_URI"), username=os.environ.get("NEO4J_USERNAME"), password=os.environ.get("NEO4J_PASSWORD"), database="stackoverflow")
```

## GraphEDA


```python
eda = GraphEDA(g)
```

We can run analytical queries individually via the `GraphEDA` class. For example let's retrieve information on the data constraints.


```python
eda.database_constraints()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>name</th>
      <th>type</th>
      <th>entityType</th>
      <th>labelsOrTypes</th>
      <th>properties</th>
      <th>ownedIndex</th>
      <th>propertyType</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20</td>
      <td>constraint_32ea8862</td>
      <td>UNIQUENESS</td>
      <td>NODE</td>
      <td>[Comment]</td>
      <td>[uuid]</td>
      <td>constraint_32ea8862</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>18</td>
      <td>constraint_401df8db</td>
      <td>UNIQUENESS</td>
      <td>NODE</td>
      <td>[Question]</td>
      <td>[uuid]</td>
      <td>constraint_401df8db</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>22</td>
      <td>constraint_64b1b1cf</td>
      <td>UNIQUENESS</td>
      <td>NODE</td>
      <td>[Tag]</td>
      <td>[name]</td>
      <td>constraint_64b1b1cf</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>19</td>
      <td>constraint_7e29bbac</td>
      <td>UNIQUENESS</td>
      <td>NODE</td>
      <td>[Answer]</td>
      <td>[uuid]</td>
      <td>constraint_7e29bbac</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>21</td>
      <td>constraint_b13a3b7d</td>
      <td>UNIQUENESS</td>
      <td>NODE</td>
      <td>[User]</td>
      <td>[uuid]</td>
      <td>constraint_b13a3b7d</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



When we run a quering method, the results are appended to an internal cache. By default we return the stored content, but we can choose to refresh the cache by providing `refresh=True`.

### Collecting Insights

We can run *all* the analytical queries in the `GraphEDA` class by calling the `run` method.

**This can be computationally intensive!**

WARNING: The methods in this module can be computationally expensive.
It is not recommended to use this module on massive Neo4j databases
(i.e., nodes and relationships in the hundreds of millions)


```python
%%capture
eda.run()
```

Now that we have our cache filled, let's see if there are any isolated nodes in the database.


```python
eda.disconnected_node_count()
```




    0



No disconnected nodes is a good sign!

## Reports

We can generate a report containing all the information we've gathered from our queries by calling `create_eda_report`.

Some of the sections can become quite lengthy, so there are arguments to control the data that is returned.


```python
%%capture
eda.create_eda_report(include_disconnected_node_ids=True, include_unlabeled_node_ids=True, include_node_degrees=True, view_report=False)
```


```python
eda.view_report(notebook=True)
```



# Runway EDA Report

## Database Information

|    | databaseName   | databaseVersion   | databaseEdition   | APOCVersion   | GDSVersion    |
|---:|:---------------|:------------------|:------------------|:--------------|:--------------|
|  0 | stackoverflow  | 5.15.0            | enterprise        | 5.15.1        | not installed |

### Counts

|    |   nodeCount |   unlabeledNodeCount |   disconnectedNodeCount |   relationshipCount |
|---:|------------:|---------------------:|------------------------:|--------------------:|
|  0 |        6193 |                    0 |                       0 |               11540 |

### Indexes

|    |   id | name                | state   |   populationPercent | type   | entityType   | labelsOrTypes   | properties   | indexProvider    | owningConstraint    | lastRead   | readCount   |
|---:|-----:|:--------------------|:--------|--------------------:|:-------|:-------------|:----------------|:-------------|:-----------------|:--------------------|:-----------|:------------|
|  0 |   17 | constraint_32ea8862 | ONLINE  |                 100 | RANGE  | NODE         | ['Comment']     | ['uuid']     | range-1.0        | constraint_32ea8862 |            |             |
|  1 |   13 | constraint_401df8db | ONLINE  |                 100 | RANGE  | NODE         | ['Question']    | ['uuid']     | range-1.0        | constraint_401df8db |            |             |
|  2 |   14 | constraint_64b1b1cf | ONLINE  |                 100 | RANGE  | NODE         | ['Tag']         | ['name']     | range-1.0        | constraint_64b1b1cf |            |             |
|  3 |   16 | constraint_7e29bbac | ONLINE  |                 100 | RANGE  | NODE         | ['Answer']      | ['uuid']     | range-1.0        | constraint_7e29bbac |            |             |
|  4 |   15 | constraint_b13a3b7d | ONLINE  |                 100 | RANGE  | NODE         | ['User']        | ['uuid']     | range-1.0        | constraint_b13a3b7d |            |             |
|  5 |    1 | index_343aff4e      | ONLINE  |                 100 | LOOKUP | NODE         |                 |              | token-lookup-1.0 |                     |            |             |
|  6 |    2 | index_f7700477      | ONLINE  |                 100 | LOOKUP | RELATIONSHIP |                 |              | token-lookup-1.0 |                     |            |             |

### Constraints

|    |   id | name                | type       | entityType   | labelsOrTypes   | properties   | ownedIndex          | propertyType   |
|---:|-----:|:--------------------|:-----------|:-------------|:----------------|:-------------|:--------------------|:---------------|
|  0 |   20 | constraint_32ea8862 | UNIQUENESS | NODE         | ['Comment']     | ['uuid']     | constraint_32ea8862 |                |
|  1 |   18 | constraint_401df8db | UNIQUENESS | NODE         | ['Question']    | ['uuid']     | constraint_401df8db |                |
|  2 |   22 | constraint_64b1b1cf | UNIQUENESS | NODE         | ['Tag']         | ['name']     | constraint_64b1b1cf |                |
|  3 |   19 | constraint_7e29bbac | UNIQUENESS | NODE         | ['Answer']      | ['uuid']     | constraint_7e29bbac |                |
|  4 |   21 | constraint_b13a3b7d | UNIQUENESS | NODE         | ['User']        | ['uuid']     | constraint_b13a3b7d |                |

## Nodes Overview
### Label Counts

|    | label    |   count |
|---:|:---------|--------:|
|  0 | Question |    1589 |
|  1 | Comment  |    1396 |
|  2 | Answer   |    1367 |
|  3 | User     |    1365 |
|  4 | Tag      |     476 |

### Properties

|    | nodeLabels   | propertyName       | propertyTypes      | mandatory   |
|---:|:-------------|:-------------------|:-------------------|:------------|
|  0 | ['User']     | uuid               | ['Long', 'String'] | True        |
|  1 | ['User']     | display_name       | ['String']         | True        |
|  2 | ['Tag']      | name               | ['String']         | True        |
|  3 | ['Tag']      | link               | ['String']         | True        |
|  4 | ['Answer']   | uuid               | ['Long']           | True        |
|  5 | ['Answer']   | title              | ['String']         | True        |
|  6 | ['Answer']   | link               | ['String']         | True        |
|  7 | ['Answer']   | is_accepted        | ['Boolean']        | True        |
|  8 | ['Answer']   | body_markdown      | ['String']         | True        |
|  9 | ['Answer']   | score              | ['Long']           | True        |
| 10 | ['Comment']  | uuid               | ['Long']           | True        |
| 11 | ['Comment']  | link               | ['String']         | True        |
| 12 | ['Comment']  | score              | ['Long']           | True        |
| 13 | ['Question'] | uuid               | ['Long']           | True        |
| 14 | ['Question'] | title              | ['String']         | True        |
| 15 | ['Question'] | creation_date      | ['Long']           | True        |
| 16 | ['Question'] | accepted_answer_id | ['Long']           | False       |
| 17 | ['Question'] | link               | ['String']         | True        |
| 18 | ['Question'] | view_count         | ['Long']           | True        |
| 19 | ['Question'] | answer_count       | ['Long']           | True        |
| 20 | ['Question'] | body_markdown      | ['String']         | True        |


## Relationships Overview
### Type Counts

|    | relType      |   count |
|---:|:-------------|--------:|
|  0 | TAGGED       |    4425 |
|  1 | ASKED        |    1589 |
|  2 | COMMENTED_ON |    1396 |
|  3 | COMMENTED    |    1396 |
|  4 | ANSWERED     |    1367 |
|  5 | PROVIDED     |    1367 |

### Properties

no relationship properties


## Unlabeled Nodes
no unlabeled nodes data in cache

## Disconnected Nodes
no disconnected nodes data in cache

## Node Degrees
* Top 5 Ordered By outDegree

|    |   nodeId | nodeLabel   |   inDegree |   outDegree |
|---:|---------:|:------------|-----------:|------------:|
|  0 |     5620 | ['User']    |          0 |         318 |
|  1 |     2441 | ['User']    |          0 |         193 |
|  2 |     2452 | ['User']    |          0 |         178 |
|  3 |     2485 | ['User']    |          0 |         144 |
|  4 |     2445 | ['User']    |          0 |         138 |

---

Runway v0.12.0

Report Generated @ 2024-10-25 10:53:46.134954



We can also save the report to a Markdown file.


```python
eda.save_report(file_name="outputs/stackoverflow_runway_report.md")
```
