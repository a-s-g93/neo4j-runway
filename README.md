# Neo4j Runway
Neo4j Runway is a Python library that simplifies the process of migrating your relational data into a graph. It provides tools that abstract communication with OpenAI to run discovery on your data and generate a data model, as well as tools to generate ingestion code and load your data into a Neo4j instance.

<img src="./docs/assets/images/neo4j-runway-logo.webp" width=300 height=400>



## Key Features

- **Data Discovery**: Harness OpenAI LLMs to provide valuable insights from your data
- **Graph Data Modeling**: Utilize OpenAI and the [Instructor](https://github.com/jxnl/instructor) Python library to create valid graph data models
- **Code Generation**: Generate ingestion code to easily load your data
- **Data Ingestion**: Load your data using Runway's built in implementation of [PyIngest](https://github.com/neo4j-field/pyingest) - Neo4j's popular ingestion tool

## Requirements
Runway uses Graphviz to visualize data models. To enjoy this feature please download [graphviz](https://www.graphviz.org/download/).

You'll need a Neo4j instance to fully utilize Runway. Start up a free cloud hosted [Aura](https://console.neo4j.io) instance or download the [Neo4j Desktop app](https://neo4j.com/download/).

## Get Running in Minutes

Follow the steps below or check out Neo4j Runway [end-to-end examples](https://github.com/a-s-g93/neo4j-runway/tree/main/examples/end_to_end)

```
pip install neo4j-runway
```

Now let's walk through a basic example.

Here we import the modules we'll be using.
```Python
from neo4j_runway import Discovery, GraphDataModeler, PyIngest, UserInput
from neo4j_runway.code_generation import PyIngestConfigGenerator
from neo4j_runway.llm.openai import OpenAIDiscoveryLLM, OpenAIDataModelingLLM

```
### Discovery
Now we...
- Define a general description of our data
- Provide brief descriptions of the columns of interest
- Provide any use cases we'd like our data model to address
- Load our csv via Runway's `load_local_files` function

```Python
data_directory = "../../../data/countries/"

data_dictionary = {
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

use_cases = [
        "Which region contains the most subregions?",
        "What currencies are most popular?",
        "Which countries share timezones?"
    ]

data = load_local_files(data_directory=data_directory,
                        data_dictionary=data_dictionary,
                        general_description="This is data on countries and their attributes.",
                        use_cases=use_cases,
                        include_files=["countries.csv"])
```

We may also preview our csv data before running any processes

```python
data.tables[0].dataframe.head()
```

<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>name</th>
      <th>phone_code</th>
      <th>capital</th>
      <th>currency_name</th>
      <th>region</th>
      <th>subregion</th>
      <th>timezones</th>
      <th>latitude</th>
      <th>longitude</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Afghanistan</td>
      <td>93</td>
      <td>Kabul</td>
      <td>Afghan afghani</td>
      <td>Asia</td>
      <td>Southern Asia</td>
      <td>[{zoneName:'Asia\/Kabul',gmtOffset:16200,gmtOf...</td>
      <td>33.000000</td>
      <td>65.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Aland Islands</td>
      <td>+358-18</td>
      <td>Mariehamn</td>
      <td>Euro</td>
      <td>Europe</td>
      <td>Northern Europe</td>
      <td>[{zoneName:'Europe\/Mariehamn',gmtOffset:7200,...</td>
      <td>60.116667</td>
      <td>19.9</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Albania</td>
      <td>355</td>
      <td>Tirana</td>
      <td>Albanian lek</td>
      <td>Europe</td>
      <td>Southern Europe</td>
      <td>[{zoneName:'Europe\/Tirane',gmtOffset:3600,gmt...</td>
      <td>41.000000</td>
      <td>20.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Algeria</td>
      <td>213</td>
      <td>Algiers</td>
      <td>Algerian dinar</td>
      <td>Africa</td>
      <td>Northern Africa</td>
      <td>[{zoneName:'Africa\/Algiers',gmtOffset:3600,gm...</td>
      <td>28.000000</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>American Samoa</td>
      <td>+1-684</td>
      <td>Pago Pago</td>
      <td>US Dollar</td>
      <td>Oceania</td>
      <td>Polynesia</td>
      <td>[{zoneName:'Pacific\/Pago_Pago',gmtOffset:-396...</td>
      <td>-14.333333</td>
      <td>-170.0</td>
    </tr>
  </tbody>
</table>
</div>


We may then initialize our discovery and data modeling LLMs. By default we use GPT-4o and define our OpenAI API key in an environment variable.

```Python
llm_disc = OpenAIDiscoveryLLM(model_name='gpt-4o-mini-2024-07-18', model_params={"temperature": 0})
llm_dm = OpenAIDataModelingLLM(model_name='gpt-4o-2024-05-13', model_params={"temperature": 0.5})
```

And we run discovery on our data.
```Python
disc = Discovery(llm=llm_disc, data=data)disc.run()

disc.run(show_result=True, notebook=True)
```
### Preliminary Analysis of Country Data

#### Overall Data Characteristics:
1. **Data Size**: The dataset contains 250 entries (countries) and 10 attributes.
2. **Data Types**: The attributes include integers, floats, and objects (strings). The presence of both numerical and categorical data allows for diverse analyses.
3. **Missing Values**:
   - `capital`: 5 missing values (2% of the data)
   - `region`: 2 missing values (0.8% of the data)
   - `subregion`: 3 missing values (1.2% of the data)
   - Other columns have no missing values.

#### Important Features:
1. **id**: Unique identifier for each country. It is uniformly distributed from 1 to 250.
2. **name**: Each country has a unique name, which is crucial for identification.
3. **phone_code**: There are 235 unique phone codes, indicating that some countries share the same code. This could be relevant for understanding regional telecommunications.
4. **capital**: The capital city is a significant attribute, but with 5 missing values, it may require attention during analysis.
5. **currency_name**: There are 161 unique currencies, with the Euro being the most common (35 occurrences). This suggests a potential clustering of countries using the same currency, which could be relevant for economic analyses.
6. **region**: There are 6 unique regions, with Africa having the highest frequency (60 countries). This could indicate a need to explore regional characteristics further.
7. **subregion**: 22 unique subregions exist, with the Caribbean being the most frequent (28 occurrences). This suggests that some regions have more subdivisions than others.
8. **timezones**: The dataset contains 245 unique timezones, indicating that many countries share timezones. This could be useful for understanding global time coordination.

#### Use Case Insights:
1. **Regions and Subregions**: To determine which region contains the most subregions, we can analyze the `region` and `subregion` columns. The region with the highest number of unique subregions will be identified.
2. **Popular Currencies**: The `currency_name` column can be analyzed to find the most frequently occurring currencies, highlighting economic ties between countries.
3. **Shared Timezones**: The `timezones` column can be examined to identify countries that share the same timezone, which may have implications for trade, communication, and travel.

### Conclusion:
The dataset provides a rich source of information about countries, their geographical locations, and economic attributes. The most important features for analysis include `region`, `subregion`, `currency_name`, and `timezones`, as they directly relate to the use cases outlined. Addressing the missing values in `capital`, `region`, and `subregion` will also be essential for a comprehensive analysis.



### Data Modeling
We can now use our Discovery object to provide context to the LLM for data model generation. Notice that we don't need to pass our actual data to the modeler, just insights we've gathered so far.

```Python
gdm = GraphDataModeler(llm=llm_dm, discovery=disc)
```

We may now generate our first graph data model.

```Python
gdm.create_initial_model()
```

If we have graphviz installed, we can take a look at our model.

```Python
gdm.current_model.visualize()
```
![countries-first-model.png](./examples/end_to_end/single_file/countries/images/countries-single-first-model-0.12.0.svg)

Our data model seems to address the three use cases we'd like answered:
* Which region contains the most subregions?
* What currencies are most popular?
* Which countries share timezones?

If we would like the data model modified, we may request the LLM to make changes.

```Python
gdm.iterate_model(corrections="Create a Capital node from the capital property.")
gdm.current_model.visualize()
```
![countries-second-model.png](./examples/end_to_end/single_file/countries/images/countries-single-second-model-0.12.0.svg)

### Code Generation
We can now use our data model to generate some ingestion code.

```Python
gen = PyIngestConfigGenerator(data_model=gdm.current_model,
                         username=os.environ.get("NEO4J_USERNAME"),
                         password=os.environ.get("NEO4J_PASSWORD"),
                         uri=os.environ.get("NEO4J_URI"),
                         database=os.environ.get("NEO4J_DATABASE"),
                         file_directory=data_directory, source_name="countries.csv")

pyingest_yaml = gen.generate_config_string()

```
### Ingestion
We will use the generated PyIngest yaml config to ingest our data into our Neo4j instance.

```Python
PyIngest(config=pyingest_yaml, verbose=False)
```

We can also save this as a .yaml file and use with the original [PyIngest](https://github.com/neo4j-field/pyingest).

```Python
gen.generate_config_yaml(file_name="countries.yaml")
```

Here's a snapshot of our new graph!

![countries-graph.png](./examples/end_to_end/single_file/countries/images/countries-single-0.12.0.png)

## Limitations
Runway is currently in beta and under rapid development. Please raise GitHub issues and provide feedback on any features you'd like. The following are some of the current limitations:
- Nodes may only have a single label
- Only uniqueness and key constraints are supported
- Only OpenAI models may be used at this time
- Runway only supports ingesting local files, though it supports code generation for other ingest methods
