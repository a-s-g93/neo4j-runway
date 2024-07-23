# Neo4j Runway
Neo4j Runway is a Python library that simplifies the process of migrating your relational data into a graph. It provides tools that abstract communication with OpenAI to run discovery on your data and generate a data model, as well as tools to generate ingestion code and load your data into a Neo4j instance.

<img src="./docs/assets/images/neo4j-runway-logo.webp" width=300 height=400> 



## Key Features

- **Data Discovery**: Harness OpenAI LLMs to provide valuable insights from your data
- **Graph Data Modeling**: Utilize OpenAI and the [Instructor](https://github.com/jxnl/instructor) Python library to create valid graph data models
- **Code Generation**: Generate ingestion code for your preferred method of loading data
- **Data Ingestion**: Load your data using Runway's built in implementation of [PyIngest](https://github.com/neo4j-field/pyingest) - Neo4j's popular ingestion tool

## Requirements
Runway uses graphviz to visualize data models. To enjoy this feature please download [graphviz](https://www.graphviz.org/download/).

You'll need a Neo4j instance to fully utilize Runway. Start up a free cloud hosted [Aura](https://console.neo4j.io) instance or download the [Neo4j Desktop app](https://neo4j.com/download/).

## Get Running in Minutes

```
pip install neo4j-runway
```

Now let's walk through a basic example.

Here we import the modules we'll be using.
```Python
import pandas as pd

from neo4j_runway import Discovery, GraphDataModeler, IngestionGenerator, LLM, PyIngest

```
### Discovery
Now we define a General Description of our data, provide brief descriptions of the columns of interest and load the data with Pandas.
```Python
USER_GENERATED_INPUT = {
    'general_description': 'This is data on different countries.',
    'id': 'unique id for a country.',
    'name': 'the country name.',
    'phone_code': 'country area code.',
    'capital': 'the capital of the country.',
    'currency_name': "name of the country's currency.",
    'region': 'primary region of the country.',
    'subregion': 'subregion location of the country.',
    'timezones': 'timezones contained within the country borders.',
    'latitude': 'the latitude coordinate of the country center.',
    'longitude': 'the longitude coordinate of the country center.'
}

data = pd.read_csv("data/csv/countries.csv")
```

We then initialize our llm. By default we use GPT-4o and define our OpenAI API key in an environment variable.
```Python
llm = LLM()
```

And we run discovery on our data.
```Python
disc = Discovery(llm=llm, user_input=USER_GENERATED_INPUT, data=data)
disc.run()
```

### Data Modeling
We can now pass our Discovery object to a GraphDataModeler to generate our initial data model. A Discovery object isn't required here, but it provides rich context to the LLM to achieve the best results.
```Python
gdm = GraphDataModeler(llm=llm, discovery=disc)
gdm.create_initial_model()
```
If we have graphviz installed, we can take a look at our model.
```Python
gdm.current_model.visualize()
```
![countries-first-model.png](./docs/assets/images/countries-first-model.png)

Let's make some corrections to our model and view the results.
```Python
gdm.iterate_model(user_corrections="""
Make Region node have a HAS_SUBREGION relationship with Subregion node. 
Remove The relationship between Country and Region.
""")
gdm.current_model.visualize()
```
![countries-second-model.png](./docs/assets/images/countries-second-model.png)

### Code Generation
We can now use our data model to generate some ingestion code.

```Python
gen = IngestionGenerator(data_model=gdm.current_model, 
                         username="neo4j", password="password", 
                         uri="bolt://localhost:7687", database="neo4j", 
                         csv_dir="data/csv/", csv_name="countries.csv")

pyingest_yaml = gen.generate_pyingest_yaml_string()

```
### Ingestion
We will use the generated PyIngest yaml config to ingest our CSV into our Neo4j instance. 
```Python
PyIngest(yaml_string=pyingest_yaml, dataframe=data)
```
We can also save this as a .yaml file and use with the original [PyIngest](https://github.com/neo4j-field/pyingest).
```Python
gen.generate_pyingest_yaml_file(file_name="countries")
```
Here's a snapshot of our new graph!

![countries-graph.png](./docs/assets/images/countries-graph-white-background.png)

## Limitations
The current project is in beta and has the following limitations:
- Single CSV input only for data model generation
- Nodes may only have a single label
- Only uniqueness and node / relationship key constraints are supported
- Relationships may not have uniqueness constraints
- CSV columns that refer to the same node property are not supported in model generation
- Only OpenAI models may be used at this time
- The modified PyIngest function included with Runway only supports loading a local Pandas DataFrame or CSVs


