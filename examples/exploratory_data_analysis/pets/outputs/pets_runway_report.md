
# Runway EDA Report

## Database Information
|    | databaseName   | databaseVersion   | databaseEdition   | APOCVersion   | GDSVersion    |
|---:|:---------------|:------------------|:------------------|:--------------|:--------------|
|  0 | neo4j          | 5.15.0            | enterprise        | 5.15.1        | not installed |

### Counts
|    |   nodeCount |   unlabeledNodeCount |   disconnectedNodeCount |   relationshipCount |
|---:|------------:|---------------------:|------------------------:|--------------------:|
|  0 |          20 |                    0 |                       1 |                  24 |

### Indexes
|    |   id | name           | state   |   populationPercent | type   | entityType   | labelsOrTypes   | properties   | indexProvider    | owningConstraint   | lastRead                            |   readCount |
|---:|-----:|:---------------|:--------|--------------------:|:-------|:-------------|:----------------|:-------------|:-----------------|:-------------------|:------------------------------------|------------:|
|  0 |    1 | index_343aff4e | ONLINE  |                 100 | LOOKUP | NODE         |                 |              | token-lookup-1.0 |                    | 2024-10-25T13:07:49.138000000+00:00 |        3809 |
|  1 |    2 | index_f7700477 | ONLINE  |                 100 | LOOKUP | RELATIONSHIP |                 |              | token-lookup-1.0 |                    |                                     |           0 |
|  2 |   33 | person_name    | ONLINE  |                 100 | RANGE  | NODE         | ['Person']      | ['name']     | range-1.0        | person_name        | 2024-10-22T18:04:42.292000000+00:00 |          55 |
|  3 |   35 | toy_name       | ONLINE  |                 100 | RANGE  | NODE         | ['Toy']         | ['name']     | range-1.0        | toy_name           | 2024-10-22T18:04:42.249000000+00:00 |          28 |

### Constraints
|    |   id | name        | type       | entityType   | labelsOrTypes   | properties   | ownedIndex   | propertyType   |
|---:|-----:|:------------|:-----------|:-------------|:----------------|:-------------|:-------------|:---------------|
|  0 |   34 | person_name | UNIQUENESS | NODE         | ['Person']      | ['name']     | person_name  |                |
|  1 |   36 | toy_name    | UNIQUENESS | NODE         | ['Toy']         | ['name']     | toy_name     |                |

## Nodes Overview
### Label Counts
|    | label   |   count |
|---:|:--------|--------:|
|  0 | Person  |       5 |
|  1 | Pet     |       5 |
|  2 | Toy     |       5 |
|  3 | Address |       4 |
|  4 | Test    |       1 |
### Multi-Label Counts
|    | labelCombinations   |   nodeCount |
|---:|:--------------------|------------:|
|  0 | ['Test', 'Label2']  |           1 |
### Properties
|    | nodeLabels         | propertyName   | propertyTypes   | mandatory   |
|---:|:-------------------|:---------------|:----------------|:------------|
|  0 | ['Label2', 'Test'] | id             | ['String']      | True        |
|  1 | ['Person']         | name           | ['String']      | True        |
|  2 | ['Person']         | age            | ['Long']        | True        |
|  3 | ['Address']        | street         | ['String']      | True        |
|  4 | ['Address']        | city           | ['String']      | True        |
|  5 | ['Pet']            | name           | ['String']      | True        |
|  6 | ['Pet']            | kind           | ['String']      | True        |
|  7 | ['Toy']            | name           | ['String']      | True        |
|  8 | ['Toy']            | kind           | ['String']      | True        |


## Relationships Overview
### Type Counts
|    | relType     |   count |
|---:|:------------|--------:|
|  0 | KNOWS       |       9 |
|  1 | HAS_ADDRESS |       5 |
|  2 | HAS_PET     |       5 |
|  3 | PLAYS_WITH  |       5 |
### Properties
no relationship properties


## Unlabeled Nodes
no unlabeled nodes data in cache
## Disconnected Nodes
|    | nodeLabel   |   nodeId |
|---:|:------------|---------:|
|  0 | Test        |   156089 |
## Node Degrees
* Top 5 Ordered By outDegree

|    |   nodeId | nodeLabel   |   inDegree |   outDegree |
|---:|---------:|:------------|-----------:|------------:|
|  0 |   156090 | ['Person']  |          3 |           4 |
|  2 |   156092 | ['Person']  |          3 |           4 |
|  3 |   156094 | ['Person']  |          0 |           4 |
|  1 |   156091 | ['Person']  |          3 |           4 |
|  4 |   156093 | ['Person']  |          0 |           3 |
---

Runway v0.12.0

Report Generated @ 2024-10-25 10:57:52.507845
