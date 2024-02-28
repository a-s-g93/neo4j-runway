This application takes a CSV file and some optional data descriptions as input and produces the following:
- Discovery on your data
- Graph data model in json format
- Ingestion code in the following formats: 
  - PyIngest yaml file
  - load_csv cypher file
  - constraints cypher file
- Database size estimation
- Automatic data loading service if Neo4j credentials are provided

A free Neo4j Aura database can be created here: https://console.neo4j.io/