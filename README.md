# Neo4j Runway
Neo4j Runway is a Python library that eases the process of migrating your relational data into a graph. It provides tools that abstract communication with OpenAI to run discovery on your data and generate a data model, as well as tools to generate ingestion code and load your data into a Neo4j instance.

## Key Features

- **LLM Assisted Data Discovery**: Harness OpenAI LLMs to provide valuable insights from your data
- **LLM Assisted Data Modeling**: Utilize OpenAI and the Instructor Python library to create valid graph data models
- **Ingestion Code Generation**: Generate ingestion code for your preferred method of loading data
- **Data Ingestion**: Load your data using Runway's built in implementation of PyIngest - Neo4j's popular ingestion tool

## Requirements
Runway uses graphviz to visualize data models. To enjoy this feature please download graphviz here[https://www.graphviz.org/download/]

You'll need a Neo4j instance to fully utilize Runway. Start up a free cloud hosted Aura instance here[https://console.neo4j.io] or download the Neo4j Desktop app here[https://neo4j.com/download/]

## Get Running in Minutes

'''
pip install neo4j-runway
'''

Now let's walk through a basic example.


Discovery
'''Python
import pandas as pd

from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.discovery import Discovery
from neo4j_runway.llm import LLM
'''
Data Model

Code Generation

Ingestion


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



