
# Runway EDA Report

## Database Information
|    | databaseName   | databaseVersion   | databaseEdition   | APOCVersion   | GDSVersion    |
|---:|:---------------|:------------------|:------------------|:--------------|:--------------|
|  0 | stackoverflow  | 5.15.0            | enterprise        | 5.15.1        | not installed |

### Counts
|    | nodeCount   |   unlabeledNodeCount |   disconnectedNodeCount | relationshipCount   |
|---:|:------------|---------------------:|------------------------:|:--------------------|
|  0 | 6,193       |                    0 |                       0 | 11,540              |

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
|    | label    | count   |
|---:|:---------|:--------|
|  0 | Question | 1,589   |
|  1 | Comment  | 1,396   |
|  2 | Answer   | 1,367   |
|  3 | User     | 1,365   |
|  4 | Tag      | 476     |
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
|    | relType      | count   |
|---:|:-------------|:--------|
|  0 | TAGGED       | 4,425   |
|  1 | ASKED        | 1,589   |
|  2 | COMMENTED_ON | 1,396   |
|  3 | COMMENTED    | 1,396   |
|  4 | ANSWERED     | 1,367   |
|  5 | PROVIDED     | 1,367   |
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

Runway v0.14.0

Report Generated @ 2024-11-04 09:52:17.872722
