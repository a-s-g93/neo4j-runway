---
permalink: /examples/countries/
title: CSV --> Graph Demo
toc: true
toc_label: 
toc_icon: "fa-solid fa-plane"
---
This notebooks demonstrates the data flow of generating a graph from a CSV file. 


```python
import os

import pandas as pd
from dotenv import load_dotenv

from neo4j_runway import Discovery, GraphDataModeler, IngestionGenerator, LLM, PyIngest
from neo4j_runway.utils import test_database_connection

load_dotenv()
```




    True



## Load and Describe Data

The USER_GENERATED_INPUT variable contains a general discription and feature descriptions for each feature we'd like to use in our graph.


```python
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
```


```python
data = pd.read_csv("data/csv/countries.csv")
```


```python
data.head()
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
      <th>iso3</th>
      <th>iso2</th>
      <th>numeric_code</th>
      <th>phone_code</th>
      <th>capital</th>
      <th>currency</th>
      <th>currency_name</th>
      <th>currency_symbol</th>
      <th>tld</th>
      <th>native</th>
      <th>region</th>
      <th>subregion</th>
      <th>timezones</th>
      <th>latitude</th>
      <th>longitude</th>
      <th>emoji</th>
      <th>emojiU</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>AF</td>
      <td>4</td>
      <td>93</td>
      <td>Kabul</td>
      <td>AFN</td>
      <td>Afghan afghani</td>
      <td>؋</td>
      <td>.af</td>
      <td>افغانستان</td>
      <td>Asia</td>
      <td>Southern Asia</td>
      <td>[{zoneName:'Asia\/Kabul',gmtOffset:16200,gmtOf...</td>
      <td>33.000000</td>
      <td>65.0</td>
      <td>🇦🇫</td>
      <td>U+1F1E6 U+1F1EB</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Aland Islands</td>
      <td>ALA</td>
      <td>AX</td>
      <td>248</td>
      <td>+358-18</td>
      <td>Mariehamn</td>
      <td>EUR</td>
      <td>Euro</td>
      <td>€</td>
      <td>.ax</td>
      <td>Åland</td>
      <td>Europe</td>
      <td>Northern Europe</td>
      <td>[{zoneName:'Europe\/Mariehamn',gmtOffset:7200,...</td>
      <td>60.116667</td>
      <td>19.9</td>
      <td>🇦🇽</td>
      <td>U+1F1E6 U+1F1FD</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Albania</td>
      <td>ALB</td>
      <td>AL</td>
      <td>8</td>
      <td>355</td>
      <td>Tirana</td>
      <td>ALL</td>
      <td>Albanian lek</td>
      <td>Lek</td>
      <td>.al</td>
      <td>Shqipëria</td>
      <td>Europe</td>
      <td>Southern Europe</td>
      <td>[{zoneName:'Europe\/Tirane',gmtOffset:3600,gmt...</td>
      <td>41.000000</td>
      <td>20.0</td>
      <td>🇦🇱</td>
      <td>U+1F1E6 U+1F1F1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Algeria</td>
      <td>DZA</td>
      <td>DZ</td>
      <td>12</td>
      <td>213</td>
      <td>Algiers</td>
      <td>DZD</td>
      <td>Algerian dinar</td>
      <td>دج</td>
      <td>.dz</td>
      <td>الجزائر</td>
      <td>Africa</td>
      <td>Northern Africa</td>
      <td>[{zoneName:'Africa\/Algiers',gmtOffset:3600,gm...</td>
      <td>28.000000</td>
      <td>3.0</td>
      <td>🇩🇿</td>
      <td>U+1F1E9 U+1F1FF</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>American Samoa</td>
      <td>ASM</td>
      <td>AS</td>
      <td>16</td>
      <td>+1-684</td>
      <td>Pago Pago</td>
      <td>USD</td>
      <td>US Dollar</td>
      <td>$</td>
      <td>.as</td>
      <td>American Samoa</td>
      <td>Oceania</td>
      <td>Polynesia</td>
      <td>[{zoneName:'Pacific\/Pago_Pago',gmtOffset:-396...</td>
      <td>-14.333333</td>
      <td>-170.0</td>
      <td>🇦🇸</td>
      <td>U+1F1E6 U+1F1F8</td>
    </tr>
  </tbody>
</table>
</div>



## Initialize LLM

We now initialize the LLM to use in data discovery and data model creation.


```python
llm = LLM()
```

## Discovery

We now load the above data into a Discovery object.


```python
disc = Discovery(llm=llm, user_input=USER_GENERATED_INPUT, data=data)
```


```python
discovery = disc.run()
print(discovery)
```

    Based on the provided summary and description of the data, here is a preliminary analysis:
    
    ### Overall Details:
    1. **Data Completeness**:
       - The dataset contains 250 entries (countries) and 10 features.
       - Most features are complete, but there are some missing values:
         - `capital`: 5 missing values.
         - `region`: 2 missing values.
         - `subregion`: 3 missing values.
    
    2. **Data Types**:
       - The dataset includes a mix of data types:
         - Numerical: `id`, `latitude`, `longitude`.
         - Categorical: `name`, `phone_code`, `capital`, `currency_name`, `region`, `subregion`, `timezones`.
    
    3. **Unique Values**:
       - `name`: All 250 entries are unique.
       - `phone_code`: 235 unique values, with the most common code appearing 3 times.
       - `capital`: 244 unique values, with one capital appearing twice.
       - `currency_name`: 161 unique values, with "Euro" being the most common (35 occurrences).
       - `region`: 6 unique values, with "Africa" being the most common (60 occurrences).
       - `subregion`: 22 unique values, with "Caribbean" being the most common (28 occurrences).
       - `timezones`: 245 unique values, with the most common timezone appearing 3 times.
    
    ### Important Features:
    1. **Geographical Coordinates**:
       - `latitude` and `longitude` provide the geographical center of each country. These features are crucial for spatial analysis and mapping.
    
    2. **Country Identification**:
       - `id` and `name` uniquely identify each country. These are essential for referencing and linking data.
    
    3. **Administrative and Political Information**:
       - `capital`: Provides the capital city, which is often a key administrative and political center.
       - `region` and `subregion`: These features categorize countries into broader geographical and political groupings, useful for regional analysis.
    
    4. **Economic Information**:
       - `currency_name`: Indicates the currency used, which can be important for economic and financial analysis.
    
    5. **Communication**:
       - `phone_code`: Provides the country’s area code, useful for telecommunications and international dialing.
    
    6. **Time Zones**:
       - `timezones`: Lists the time zones within each country, which is important for understanding temporal differences and scheduling across regions.
    
    ### Summary:
    - The dataset is relatively complete with only a few missing values.
    - It contains a mix of numerical and categorical data, with unique identifiers for each country.
    - Key features include geographical coordinates, administrative information (capital, region, subregion), economic data (currency), and communication details (phone code, timezones).
    - The data is well-suited for geographical, political, and economic analysis, and can be used to explore relationships between countries based on these features.
    
    This preliminary analysis provides a foundation for further exploration and potential modeling, including the creation of a graph data model.


## Data Modeling

We can now use our Discovery object to provide context to the LLM for data model generation. We don't *need* the discovery information for this step to work, but it provides much better models.


```python
gdm = GraphDataModeler(
    llm=llm,
    discovery=disc
)
```

We now generate our first pass data model.


```python
gdm.create_initial_model()
```

    recieved a valid response



```python
gdm.current_model
```




    DataModel(nodes=[Node(label='Country', properties=[Property(name='id', type='int', csv_mapping='id', is_unique=True, part_of_key=False), Property(name='name', type='str', csv_mapping='name', is_unique=False, part_of_key=False)], csv_name=''), Node(label='Capital', properties=[Property(name='capitalName', type='str', csv_mapping='capital', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Currency', properties=[Property(name='currencyName', type='str', csv_mapping='currency_name', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Region', properties=[Property(name='regionName', type='str', csv_mapping='region', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Subregion', properties=[Property(name='subregionName', type='str', csv_mapping='subregion', is_unique=True, part_of_key=False)], csv_name=''), Node(label='PhoneCode', properties=[Property(name='phoneCode', type='str', csv_mapping='phone_code', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Timezone', properties=[Property(name='timezone', type='str', csv_mapping='timezones', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Geolocation', properties=[Property(name='latitude', type='float', csv_mapping='latitude', is_unique=False, part_of_key=True), Property(name='longitude', type='float', csv_mapping='longitude', is_unique=False, part_of_key=True)], csv_name='')], relationships=[Relationship(type='HAS_CAPITAL', properties=[], source='Country', target='Capital', csv_name=''), Relationship(type='USES_CURRENCY', properties=[], source='Country', target='Currency', csv_name=''), Relationship(type='BELONGS_TO_REGION', properties=[], source='Country', target='Region', csv_name=''), Relationship(type='BELONGS_TO_SUBREGION', properties=[], source='Country', target='Subregion', csv_name=''), Relationship(type='HAS_PHONE_CODE', properties=[], source='Country', target='PhoneCode', csv_name=''), Relationship(type='HAS_TIMEZONE', properties=[], source='Country', target='Timezone', csv_name=''), Relationship(type='HAS_GEOLOCATION', properties=[], source='Country', target='Geolocation', csv_name='')])




```python
gdm.current_model.visualize()
```




    
![svg](output_20_0.svg)
    



This doesn't look quite right, so let's prompt the LLM to make some corrections.


```python
gdm.iterate_model(user_corrections="Make Region node have a HAS_SUBREGION relationship with Subregion node. Remove The relationship between Country and Region. Both the latitude and longitude properties on Geolocation should remain node keys.")
```

    recieved a valid response





    DataModel(nodes=[Node(label='Country', properties=[Property(name='id', type='int', csv_mapping='id', is_unique=True, part_of_key=False), Property(name='name', type='str', csv_mapping='name', is_unique=False, part_of_key=False)], csv_name=''), Node(label='Capital', properties=[Property(name='capitalName', type='str', csv_mapping='capital', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Currency', properties=[Property(name='currencyName', type='str', csv_mapping='currency_name', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Region', properties=[Property(name='regionName', type='str', csv_mapping='region', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Subregion', properties=[Property(name='subregionName', type='str', csv_mapping='subregion', is_unique=True, part_of_key=False)], csv_name=''), Node(label='PhoneCode', properties=[Property(name='phoneCode', type='str', csv_mapping='phone_code', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Timezone', properties=[Property(name='timezone', type='str', csv_mapping='timezones', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Geolocation', properties=[Property(name='latitude', type='float', csv_mapping='latitude', is_unique=False, part_of_key=True), Property(name='longitude', type='float', csv_mapping='longitude', is_unique=False, part_of_key=True)], csv_name='')], relationships=[Relationship(type='HAS_CAPITAL', properties=[], source='Country', target='Capital', csv_name=''), Relationship(type='USES_CURRENCY', properties=[], source='Country', target='Currency', csv_name=''), Relationship(type='BELONGS_TO_SUBREGION', properties=[], source='Country', target='Subregion', csv_name=''), Relationship(type='HAS_PHONE_CODE', properties=[], source='Country', target='PhoneCode', csv_name=''), Relationship(type='HAS_TIMEZONE', properties=[], source='Country', target='Timezone', csv_name=''), Relationship(type='HAS_GEOLOCATION', properties=[], source='Country', target='Geolocation', csv_name=''), Relationship(type='HAS_SUBREGION', properties=[], source='Region', target='Subregion', csv_name='')])




```python
gdm.current_model
```




    DataModel(nodes=[Node(label='Country', properties=[Property(name='id', type='int', csv_mapping='id', is_unique=True, part_of_key=False), Property(name='name', type='str', csv_mapping='name', is_unique=False, part_of_key=False)], csv_name=''), Node(label='Capital', properties=[Property(name='capitalName', type='str', csv_mapping='capital', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Currency', properties=[Property(name='currencyName', type='str', csv_mapping='currency_name', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Region', properties=[Property(name='regionName', type='str', csv_mapping='region', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Subregion', properties=[Property(name='subregionName', type='str', csv_mapping='subregion', is_unique=True, part_of_key=False)], csv_name=''), Node(label='PhoneCode', properties=[Property(name='phoneCode', type='str', csv_mapping='phone_code', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Timezone', properties=[Property(name='timezone', type='str', csv_mapping='timezones', is_unique=True, part_of_key=False)], csv_name=''), Node(label='Geolocation', properties=[Property(name='latitude', type='float', csv_mapping='latitude', is_unique=False, part_of_key=True), Property(name='longitude', type='float', csv_mapping='longitude', is_unique=False, part_of_key=True)], csv_name='')], relationships=[Relationship(type='HAS_CAPITAL', properties=[], source='Country', target='Capital', csv_name=''), Relationship(type='USES_CURRENCY', properties=[], source='Country', target='Currency', csv_name=''), Relationship(type='BELONGS_TO_SUBREGION', properties=[], source='Country', target='Subregion', csv_name=''), Relationship(type='HAS_PHONE_CODE', properties=[], source='Country', target='PhoneCode', csv_name=''), Relationship(type='HAS_TIMEZONE', properties=[], source='Country', target='Timezone', csv_name=''), Relationship(type='HAS_GEOLOCATION', properties=[], source='Country', target='Geolocation', csv_name=''), Relationship(type='HAS_SUBREGION', properties=[], source='Region', target='Subregion', csv_name='')])




```python
gdm.current_model.visualize()
```




    
![svg](output_24_0.svg)
    



This is good enough for our demo. We can now create some ingestion code to get our data into our database.

## Ingestion Code Generation

We can provide our credentials here in this step if we plan on using PyIngest to load our data. This will inject our credentials into the generated YAML file. If we leave the credential fields blank, then we can just fill in the blanks in the generated YAML file later.


```python

gen = IngestionGenerator(data_model=gdm.current_model, 
                         username=os.environ.get("NEO4J_USERNAME"), 
                         password=os.environ.get("NEO4J_PASSWORD"), 
                         uri=os.environ.get("NEO4J_URI"), 
                         database=os.environ.get("NEO4J_DATABASE"), 
                         csv_dir="data/csv/", csv_name="countries.csv")
```


```python
pyingest_yaml = gen.generate_pyingest_yaml_string()
# gen.generate_pyingest_yaml_file(file_name="countries")
print(pyingest_yaml)
```

    server_uri: bolt://localhost:7687
    admin_user: neo4j
    admin_pass: password
    database: neo4j
    basepath: ./
    
    pre_ingest:
      - CREATE CONSTRAINT country_id IF NOT EXISTS FOR (n:Country) REQUIRE n.id IS UNIQUE;
      - CREATE CONSTRAINT capital_capitalname IF NOT EXISTS FOR (n:Capital) REQUIRE n.capitalName IS UNIQUE;
      - CREATE CONSTRAINT currency_currencyname IF NOT EXISTS FOR (n:Currency) REQUIRE n.currencyName IS UNIQUE;
      - CREATE CONSTRAINT region_regionname IF NOT EXISTS FOR (n:Region) REQUIRE n.regionName IS UNIQUE;
      - CREATE CONSTRAINT subregion_subregionname IF NOT EXISTS FOR (n:Subregion) REQUIRE n.subregionName IS UNIQUE;
      - CREATE CONSTRAINT phonecode_phonecode IF NOT EXISTS FOR (n:PhoneCode) REQUIRE n.phoneCode IS UNIQUE;
      - CREATE CONSTRAINT timezone_timezone IF NOT EXISTS FOR (n:Timezone) REQUIRE n.timezone IS UNIQUE;
      - CREATE CONSTRAINT geolocation_latitude_longitude IF NOT EXISTS FOR (n:Geolocation) REQUIRE (n.latitude, n.longitude) IS NODE KEY;
    files:
    - chunk_size: 100
      cql: |-
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Country {id: row.id})
        SET n.name = row.name
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Capital {capitalName: row.capital})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Currency {currencyName: row.currency_name})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Region {regionName: row.region})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Subregion {subregionName: row.subregion})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:PhoneCode {phoneCode: row.phone_code})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Timezone {timezone: row.timezones})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows AS row
        MERGE (n:Geolocation {latitude: row.latitude, longitude: row.longitude})
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:Capital {capitalName: row.capital})
        MERGE (source)-[n:HAS_CAPITAL]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:Currency {currencyName: row.currency_name})
        MERGE (source)-[n:USES_CURRENCY]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:Subregion {subregionName: row.subregion})
        MERGE (source)-[n:BELONGS_TO_SUBREGION]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:PhoneCode {phoneCode: row.phone_code})
        MERGE (source)-[n:HAS_PHONE_CODE]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:Timezone {timezone: row.timezones})
        MERGE (source)-[n:HAS_TIMEZONE]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Country {id: row.id})
        MATCH (target:Geolocation {latitude: row.latitude, longitude: row.longitude})
        MERGE (source)-[n:HAS_GEOLOCATION]->(target)
      url: $BASE/data/csv/countries.csv
    - chunk_size: 100
      cql: |
        WITH $dict.rows AS rows
        UNWIND rows as row
        MATCH (source:Region {regionName: row.region})
        MATCH (target:Subregion {subregionName: row.subregion})
        MERGE (source)-[n:HAS_SUBREGION]->(target)
      url: $BASE/data/csv/countries.csv
    


## Ingest Data

We can use the generated yaml string above to orchestrate the data loading via a modified PyIngest function. First let's confirm our connection though.


```python
test_database_connection(credentials={"username": os.environ.get("NEO4J_USERNAME"), "password": os.environ.get("NEO4J_PASSWORD"), "uri": os.environ.get("NEO4J_URI")})
```




    {'valid': True, 'message': 'Connection and Auth Verified!'}




```python
PyIngest(yaml_string=pyingest_yaml, dataframe=data)
```

    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:23.860265
    loading... 1 2024-05-20 14:05:23.936473
    {} : Completed file 2024-05-20 14:05:23.958260
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:23.958827
    loading... 1 2024-05-20 14:05:23.990325
    {} : Completed file 2024-05-20 14:05:24.008697
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.009208
    loading... 1 2024-05-20 14:05:24.038214
    {} : Completed file 2024-05-20 14:05:24.056043
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.056455


    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)


    loading... 1 2024-05-20 14:05:24.083988
    {} : Completed file 2024-05-20 14:05:24.095477
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.095866
    loading... 1 2024-05-20 14:05:24.129623
    {} : Completed file 2024-05-20 14:05:24.141679
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.142192
    loading... 1 2024-05-20 14:05:24.171952
    {} : Completed file 2024-05-20 14:05:24.190068
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.190598
    loading... 1 2024-05-20 14:05:24.221659
    {} : Completed file 2024-05-20 14:05:24.240913
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.241376
    loading... 1 2024-05-20 14:05:24.270959
    {} : Completed file 2024-05-20 14:05:24.289059
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.289576


    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)


    loading... 1 2024-05-20 14:05:24.327192
    {} : Completed file 2024-05-20 14:05:24.343518
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.344110
    loading... 1 2024-05-20 14:05:24.378096
    {} : Completed file 2024-05-20 14:05:24.396121
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.396630
    loading... 1 2024-05-20 14:05:24.431194
    {} : Completed file 2024-05-20 14:05:24.447650
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.448132
    loading... 1 2024-05-20 14:05:24.499250
    {} : Completed file 2024-05-20 14:05:24.517146
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.517540


    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)


    loading... 1 2024-05-20 14:05:24.552907
    {} : Completed file 2024-05-20 14:05:24.573239
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.573867
    loading... 1 2024-05-20 14:05:24.628128
    {} : Completed file 2024-05-20 14:05:24.652196
    File {} .//data/csv/countries.csv
    loading... 0 2024-05-20 14:05:24.652724
    loading... 1 2024-05-20 14:05:24.684485
    {} : Completed file 2024-05-20 14:05:24.695933


    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)
    /Users/alexandergilmore/Documents/projects/neo4j-runway-examples/venv/lib/python3.12/site-packages/numpy/core/fromnumeric.py:59: FutureWarning: 'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose' instead.
      return bound(*args, **kwds)


If we check our database we can see that we've ingested our CSV according to the data model we've created!

![countries-graph-0.2.0.png](./images/countries-graph-0.2.0.png)


