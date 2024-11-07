
# Runway EDA Report

## Database Information
|    | databaseName   | databaseVersion   | databaseEdition   | APOCVersion   | GDSVersion    |
|---:|:---------------|:------------------|:------------------|:--------------|:--------------|
|  0 | neo4j          | 5.15.0            | enterprise        | 5.15.1        | not installed |

### Counts
|    | nodeCount   |   unlabeledNodeCount |   disconnectedNodeCount | relationshipCount   |
|---:|:------------|---------------------:|------------------------:|:--------------------|
|  0 | 155,979     |                   20 |                      12 | 156,025             |

### Indexes
|    |   id | name                    | state   |   populationPercent | type   | entityType   | labelsOrTypes   | properties        | indexProvider    | owningConstraint        | lastRead                            | readCount   |
|---:|-----:|:------------------------|:--------|--------------------:|:-------|:-------------|:----------------|:------------------|:-----------------|:------------------------|:------------------------------------|:------------|
|  0 |    5 | city_cityid             | ONLINE  |                 100 | RANGE  | NODE         | ['City']        | ['cityId']        | range-1.0        | city_cityid             | 2024-11-04T15:24:23.674000000+00:00 | 601,816     |
|  1 |    7 | country_countryid       | ONLINE  |                 100 | RANGE  | NODE         | ['Country']     | ['countryId']     | range-1.0        | country_countryid       | 2024-11-04T15:24:23.849000000+00:00 | 6,327       |
|  2 |   11 | currency_currencyname   | ONLINE  |                 100 | RANGE  | NODE         | ['Currency']    | ['currencyName']  | range-1.0        | currency_currencyname   | 2024-11-04T15:24:23.849000000+00:00 | 812         |
|  3 |    1 | index_343aff4e          | ONLINE  |                 100 | LOOKUP | NODE         |                 |                   | token-lookup-1.0 |                         | 2024-11-04T22:18:30.537000000+00:00 | 4,052       |
|  4 |    2 | index_f7700477          | ONLINE  |                 100 | LOOKUP | RELATIONSHIP |                 |                   | token-lookup-1.0 |                         |                                     | 0           |
|  5 |   13 | region_regionname       | ONLINE  |                 100 | RANGE  | NODE         | ['Region']      | ['regionName']    | range-1.0        | region_regionname       | 2024-11-04T15:24:23.931000000+00:00 | 514         |
|  6 |    3 | state_stateid           | ONLINE  |                 100 | RANGE  | NODE         | ['State']       | ['stateId']       | range-1.0        | state_stateid           | 2024-11-04T15:24:23.674000000+00:00 | 170,762     |
|  7 |    9 | subregion_subregionname | ONLINE  |                 100 | RANGE  | NODE         | ['Subregion']   | ['subregionName'] | range-1.0        | subregion_subregionname | 2024-11-04T15:24:23.931000000+00:00 | 796         |

### Constraints
|    |   id | name                    | type       | entityType   | labelsOrTypes   | properties        | ownedIndex              | propertyType   |
|---:|-----:|:------------------------|:-----------|:-------------|:----------------|:------------------|:------------------------|:---------------|
|  0 |    6 | city_cityid             | UNIQUENESS | NODE         | ['City']        | ['cityId']        | city_cityid             |                |
|  1 |    8 | country_countryid       | UNIQUENESS | NODE         | ['Country']     | ['countryId']     | country_countryid       |                |
|  2 |   12 | currency_currencyname   | UNIQUENESS | NODE         | ['Currency']    | ['currencyName']  | currency_currencyname   |                |
|  3 |   14 | region_regionname       | UNIQUENESS | NODE         | ['Region']      | ['regionName']    | region_regionname       |                |
|  4 |    4 | state_stateid           | UNIQUENESS | NODE         | ['State']       | ['stateId']       | state_stateid           |                |
|  5 |   10 | subregion_subregionname | UNIQUENESS | NODE         | ['Subregion']   | ['subregionName'] | subregion_subregionname |                |

## Nodes Overview
### Label Counts
|    | label        | count   |
|---:|:-------------|:--------|
|  0 | City         | 150,434 |
|  1 | State        | 5,077   |
|  2 | Country      | 250     |
|  3 | Currency     | 156     |
|  4 | Subregion    | 23      |
|  5 | IsolatedNode | 12      |
|  6 | Region       | 7       |
|  7 |              | 0       |
### Properties
|    | nodeLabels       | propertyName   | propertyTypes   | mandatory   |
|---:|:-----------------|:---------------|:----------------|:------------|
|  0 | []               | name           | ['String']      | True        |
|  1 | []               | cityId         | ['String']      | True        |
|  2 | ['City']         | name           | ['String']      | True        |
|  3 | ['City']         | cityId         | ['String']      | True        |
|  4 | ['IsolatedNode'] | id             | ['Long']        | False       |
|  5 | ['Region']       | regionName     | ['String']      | True        |
|  6 | ['State']        | name           | ['String']      | True        |
|  7 | ['State']        | stateId        | ['String']      | True        |
|  8 | ['Country']      | name           | ['String']      | True        |
|  9 | ['Country']      | capital        | ['String']      | True        |
| 10 | ['Country']      | countryId      | ['String']      | True        |
| 11 | ['Subregion']    | subregionName  | ['String']      | True        |
| 12 | ['Currency']     | currencyName   | ['String']      | True        |


## Relationships Overview
### Type Counts
|    | relType    | count   |
|---:|:-----------|:--------|
|  0 | LOCATED_IN | 150,454 |
|  1 | BELONGS_TO | 5,047   |
|  2 | PART_OF    | 274     |
|  3 | USES       | 250     |
### Properties
|    | relType       | propertyName   | propertyTypes   | mandatory   |
|---:|:--------------|:---------------|:----------------|:------------|
|  0 | :`BELONGS_TO` | demo_prop      | ['Double']      | False       |


## Unlabeled Nodes
|    | ids   |
|---:|:------|
|  0 | 5,077 |
|  1 | 5,078 |
|  2 | 5,079 |
|  3 | 5,080 |
|  4 | 5,081 |
|  5 | 5,082 |
|  6 | 5,083 |
|  7 | 5,084 |
|  8 | 5,085 |
|  9 | 5,086 |
| 10 | 5,087 |
| 11 | 5,088 |
| 12 | 5,089 |
| 13 | 5,090 |
| 14 | 5,091 |
| 15 | 5,092 |
| 16 | 5,093 |
| 17 | 5,094 |
| 18 | 5,095 |
| 19 | 5,096 |
## Disconnected Nodes
|    | nodeLabel    | nodeId   |
|---:|:-------------|:---------|
|  0 | IsolatedNode | 155,967  |
|  1 | IsolatedNode | 155,968  |
|  2 | IsolatedNode | 155,969  |
|  3 | IsolatedNode | 155,970  |
|  4 | IsolatedNode | 155,971  |
|  5 | IsolatedNode | 155,972  |
|  6 | IsolatedNode | 155,973  |
|  7 | IsolatedNode | 155,974  |
|  8 | IsolatedNode | 155,975  |
|  9 | IsolatedNode | 155,976  |
| 10 | IsolatedNode | 155,977  |
| 11 | IsolatedNode | 155,978  |
## Node Degrees
* Top 5 Ordered By inDegree

|    |   nodeId | nodeLabel   |   inDegree |   outDegree |
|---:|---------:|:------------|-----------:|------------:|
|  0 |     4671 | ['State']   |       2919 |           1 |
|  1 |     1843 | ['State']   |       1787 |           1 |
|  2 |     1384 | ['State']   |       1756 |           1 |
|  3 |     1865 | ['State']   |       1289 |           1 |
|  4 |     4886 | ['State']   |       1277 |           1 |
---

Runway v0.14.0

Report Generated @ 2024-11-04 16:23:33.445064
