import json
from typing import Dict, List, Any, Union
import csv
import os
import argparse
import yaml
from yaml.representer import SafeRepresenter

from pydantic import BaseModel

cypher_map ={}
model_maps = []
nodes_map = {}
create_constraints = {}

missing_properties_err = []

class folded_unicode(str): pass
class literal_unicode(str): pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)

def lowercase_first_letter(str):
  return str[0].lower() + str[1:]


class IngestionGenerator(BaseModel):

  data_model: Dict[str, Any]
  username: str
  password: str
  uri: str
  database: str
  csv_file_path: Union[str, None]

  config_files_list: Union[List[Dict[str, Any]], None] = []
  constraints: Dict[str, str] = {}
  cypher_map: Dict[str, Dict[str, Any]] = {}

  def __init__(self, *a, **kw):
      super().__init__(*a, **kw)

      self._generate_base_information()

  def _generate_base_information(self):
    for node in self.data_model["nodes"]:
          label = node["label"]
          props = node["properties"]
          if "," in node["unique_constraints"]:
            uniq_constraints_parts = node["unique_constraints"].split(",")
          elif len(node["unique_constraints"]) > 0:
            uniq_constraints_parts = node["unique_constraints"]
          else:
            missing_properties_err.append({"label" : label})
          
          props = list(set(props) - set(node["unique_constraints"]))
          csv_file = self.csv_file_path
          uniq_constraints = []
          non_uniq_constraints = []
    
          if len(uniq_constraints_parts) > 0:
            for part in uniq_constraints_parts:
              constraint_prop_name = part.lower()
              uniq_constraints.append(f"{constraint_prop_name}: row.{part}")
              self.constraints[f"{label.lower()}_{constraint_prop_name}"] = f"CREATE CONSTRAINT {label.lower()}_{constraint_prop_name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{constraint_prop_name} IS UNIQUE;\n"

          #use first property as unique constraint, at this time
          for count, prop in enumerate(props):
            property_name = prop.lower()
            non_uniq_constraints.append(f"n.{property_name} = row.{prop}") 

          uniq_constr_str = ", ".join(uniq_constraints)
          print(f"uniq_constr_str: {uniq_constr_str}")

          non_uniq_constr_str = ", ".join(non_uniq_constraints)
          if not non_uniq_constr_str == "":
            non_uniq_constr_str = f"SET {non_uniq_constr_str}"

          merge_str = "WITH $dict.rows AS rows\nUNWIND rows AS row\nMERGE (n:" + label + " {" + uniq_constr_str + "})\n" + non_uniq_constr_str 
          load_csv_merge_str = "LOAD CSV WITH HEADERS FROM 'file:///file_name' as row\nCALL {\n\tWITH row\n\tMERGE (n:" + label + " {" + uniq_constr_str + "})\n" + non_uniq_constr_str + "} IN TRANSACTIONS OF 10000 ROWS;\n"
          #print(load_csv_merge_str)
          nodes_map[lowercase_first_letter(label)] = "MATCH (n:" + label + "{" + f"{uniq_constr_str}" + "})"
                
          #add to cypher map
          self.cypher_map[lowercase_first_letter(label)] = {"cypher" : literal_unicode(merge_str), "cypher_loadcsv": literal_unicode(load_csv_merge_str), "csv": f"$BASE/data/{csv_file}" }

    model_map = {}    
    ## get relationships
    for rel in self.data_model["relationships"]:
      rel_type = rel["type"]
      src_node_label = rel["source"]
      target_node_label = rel["target"]
      model_map[f"{lowercase_first_letter(src_node_label)}_{lowercase_first_letter(target_node_label)}"] = { \
        "source": {"node": f"{nodes_map[lowercase_first_letter(src_node_label)]}"},
        "target": {"node": f"{nodes_map[lowercase_first_letter(target_node_label)]}"},
        "csv": f"{self.csv_file_path}",
        "relationship": {"rel": rel_type}
      }
      model_maps.append(model_map)
      for mapitem in model_map:
        if not model_map[mapitem]["csv"] is None:
          merge_str = f"WITH $dict.rows AS rows\nUNWIND rows as row\n" \
                    f"{model_map[mapitem]['source']['node'].replace('n:', 'source:')}\n" \
                    f"{model_map[mapitem]['target']['node'].replace('n:', 'target:')}\n" \
                    f"MERGE (source)-[:{model_map[mapitem]['relationship']['rel']}]->(target)" 
          newline = "\n"
          tab = "\t"
          load_csv_merge_str = f"LOAD CSV WITH HEADERS FROM 'file:///file_name' as row{newline}" \
                    f"CALL {{{newline}{tab}WITH row{newline}" \
                    f"{tab}{model_map[mapitem]['source']['node'].replace('n:', 'source:')}{newline}" \
                    f"{tab}{model_map[mapitem]['target']['node'].replace('n:', 'target:')}{newline}" \
                    f"{tab}MERGE (source)-[:{model_map[mapitem]['relationship']['rel']}]->(target){newline}}} IN TRANSACTIONS OF 10000 ROWS;{newline}"

          #print(load_csv_merge_str)
          self.cypher_map[mapitem] = {"cypher": literal_unicode(merge_str), "cypher_loadcsv": literal_unicode(load_csv_merge_str),  "csv": f"$BASE/data/{model_map[mapitem]['csv']}" }
  
    #print(self.cypher_map)
    self.config_files_list = []
    for item in self.cypher_map:
      file_dict = {}
      if self.cypher_map[item]["csv"]:
        file_dict["url"] = self.cypher_map[item]["csv"]
        file_dict["cql"] = self.cypher_map[item]["cypher"]
        file_dict["chunk_size"] =  100 
        self.config_files_list.append(file_dict)

    print(self.config_files_list)

    self.config_files_list = []
    for item in self.cypher_map:
      file_dict = {}
      if self.cypher_map[item]["csv"]:
        file_dict["url"] = self.cypher_map[item]["csv"]
        file_dict["cql"] = self.cypher_map[item]["cypher"]
        file_dict["chunk_size"] =  100 
        self.config_files_list.append(file_dict)

  def generate_pyingest_yaml(self) -> None:
    """
    Generate the PyIngest yaml file.
    """
    #create pyingest config.yml
    final_yaml = {}
    final_yaml["files"] = self.config_files_list
    config_dump = yaml.dump(final_yaml)
    with open("./pyingest_config.yml", "w") as config_yaml:
      config_yaml.write(f"server_uri: {self.uri}\n")
      config_yaml.write(f"admin_user: {self.username}\n")
      config_yaml.write(f"admin_pass: {self.password}\n")
      config_yaml.write("basepath: file:./\n\n")
      config_yaml.write("pre_ingest:\n")
      for constraint in self.constraints:
        config_yaml.write(f"  - {self.constraints[constraint]}")
      config_yaml.write(config_dump)
 
  def generate_constraints_cypher(self) -> None:
    """
    Generate the Constraints cypher file.
    """
    #create constraints cypher
    with open("./constraints.cypher", "w") as constraints_cypher:
      for constraint in self.constraints:
        constraints_cypher.write(self.constraints[constraint])

  def generate_load_csv(self) -> None:
    """
    Generate the load_csv cypher file.
    """
    load_csv = []
    for item in self.cypher_map:
      load_csv.append(self.cypher_map[item]["cypher_loadcsv"])
      #config_files_list.append(file_dict)

    with open("./load_csv.cypher", "w") as load_csv_file:
      load_csv_file.writelines([f"{self.constraints[constraint]}\n" for constraint in self.constraints])
      load_csv_file.writelines([f"{line}\n" for line in load_csv])


def create_from_datamodel(args):
  with open(args.modelfile) as f:
    model_json = json.load(f)
    for node in model_json["Nodes"]:
      label = node["Label"]
      props = node["Properties"]
      if "," in node["unique_constraints"]:
        uniq_constraints_parts = node["unique_constraints"].split(",")
      elif len(node["unique_constraints"]) > 0:
        uniq_constraints_parts = node["unique_constraints"]
      else:
        missing_properties_err.append({"label" : label})
      
      props = list(set(props) - set(node["unique_constraints"]))
      csv_file = args.csv_file 
      uniq_constraints = []
      non_uniq_constraints = []
 
      if len(uniq_constraints_parts) > 0:
        for part in uniq_constraints_parts:
          constraint_prop_name = part.lower()
          uniq_constraints.append(f"{constraint_prop_name}: row.{part}")
          create_constraints[f"{label.lower()}_{constraint_prop_name}"] = f"CREATE CONSTRAINT {label.lower()}_{constraint_prop_name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{constraint_prop_name} IS UNIQUE;\n"

      #use first property as unique constraint, at this time
      for count, prop in enumerate(props):
        property_name = prop.lower()
        non_uniq_constraints.append(f"n.{property_name} = row.{prop}") 

      uniq_constr_str = ", ".join(uniq_constraints)
      print(f"uniq_constr_str: {uniq_constr_str}")

      non_uniq_constr_str = ", ".join(non_uniq_constraints)
      if not non_uniq_constr_str == "":
        non_uniq_constr_str = f"SET {non_uniq_constr_str}"

      merge_str = "WITH $dict.rows AS rows\nUNWIND rows AS row\nMERGE (n:" + label + " {" + uniq_constr_str + "})\n" + non_uniq_constr_str 
      load_csv_merge_str = "LOAD CSV WITH HEADERS FROM 'file:///file_name' as row\nCALL {\n\tWITH row\n\tMERGE (n:" + label + " {" + uniq_constr_str + "})\n" + non_uniq_constr_str + "} IN TRANSACTIONS OF 10000 ROWS;\n"
      #print(load_csv_merge_str)
      nodes_map[lowercase_first_letter(label)] = "MATCH (n:" + label + "{" + f"{uniq_constr_str}" + "})"
            
      #add to cypher map
      cypher_map[lowercase_first_letter(label)] = {"cypher" : literal_unicode(merge_str), "cypher_loadcsv": literal_unicode(load_csv_merge_str), "csv": f"$BASE/data/{csv_file}" }

    model_map = {}    
    ## get relationships
    for rel in model_json["Relationships"]:
      rel_type = rel["Type"]
      src_node_label = rel["From"]
      target_node_label = rel["To"]
      model_map[f"{lowercase_first_letter(src_node_label)}_{lowercase_first_letter(target_node_label)}"] = { \
        "source": {"node": f"{nodes_map[lowercase_first_letter(src_node_label)]}"},
        "target": {"node": f"{nodes_map[lowercase_first_letter(target_node_label)]}"},
        "csv": f"{args.csv_file}",
        "relationship": {"rel": rel_type}
      }
      model_maps.append(model_map)
      for mapitem in model_map:
        if not model_map[mapitem]["csv"] is None:
          merge_str = f"WITH $dict.rows AS rows\nUNWIND rows as row\n" \
                    f"{model_map[mapitem]['source']['node'].replace('n:', 'source:')}\n" \
                    f"{model_map[mapitem]['target']['node'].replace('n:', 'target:')}\n" \
                    f"MERGE (source)-[:{model_map[mapitem]['relationship']['rel']}]->(target)" 
          newline = "\n"
          tab = "\t"
          load_csv_merge_str = f"LOAD CSV WITH HEADERS FROM 'file:///file_name' as row{newline}" \
                    f"CALL {{{newline}{tab}WITH row{newline}" \
                    f"{tab}{model_map[mapitem]['source']['node'].replace('n:', 'source:')}{newline}" \
                    f"{tab}{model_map[mapitem]['target']['node'].replace('n:', 'target:')}{newline}" \
                    f"{tab}MERGE (source)-[:{model_map[mapitem]['relationship']['rel']}]->(target){newline}}} IN TRANSACTIONS OF 10000 ROWS;{newline}"

          #print(load_csv_merge_str)
          cypher_map[mapitem] = {"cypher": literal_unicode(merge_str), "cypher_loadcsv": literal_unicode(load_csv_merge_str),  "csv": f"$BASE/data/{model_map[mapitem]['csv']}" }
  
  #print(cypher_map)
  config_files_list = []
  for item in cypher_map:
    file_dict = {}
    if cypher_map[item]["csv"]:
      file_dict["url"] = cypher_map[item]["csv"]
      file_dict["cql"] = cypher_map[item]["cypher"]
      file_dict["chunk_size"] =  100 
      config_files_list.append(file_dict)

  #create pyingest config.yml
  final_yaml = {}
  final_yaml["files"] = config_files_list
  config_dump = yaml.dump(final_yaml)
  with open("./output/config.yml", "w") as config_yaml:
    config_yaml.write(f"server_uri: {args.uri}\n")
    config_yaml.write(f"admin_user: {args.username}\n")
    config_yaml.write(f"admin_pass: {args.password}\n")
    config_yaml.write("basepath: file:./\n\n")
    config_yaml.write("pre_ingest:\n")
    for constraint in create_constraints:
      config_yaml.write(f"  - {create_constraints[constraint]}")
    config_yaml.write(config_dump)
 
  #create constraints cypher
  with open("./output/constraints.cypher", "w") as constraints_cypher:
    for constraint in create_constraints:
      constraints_cypher.write(create_constraints[constraint])

  load_csv = []
  for item in cypher_map:
    load_csv.append(cypher_map[item]["cypher_loadcsv"])
    #config_files_list.append(file_dict)

  with open("./output/load_csv.cypher", "w") as load_csv_file:
    load_csv_file.writelines([f"{create_constraints[constraint]}\n" for constraint in create_constraints])
    load_csv_file.writelines([f"{line}\n" for line in load_csv])

# if __name__ == '__main__':

#   parser = argparse.ArgumentParser()
#   parser.add_argument("--modelfile", required=True)
#   parser.add_argument("--uri", required=True)
#   parser.add_argument("--csv_file", required=True)
#   parser.add_argument("--username", required=True)
#   parser.add_argument("--password", required=True)

#   args = parser.parse_args()

#   create_from_datamodel(args)

#   print("\n")
#   print("*** generated pyingest config.yml file")
#   print("*** generated load_csv.cypher file")
#   #print labels missing properties
#   print("\n")
#   print("The following labels were missing properties, therefore an ingest wasn't generated for them:")
#   [print(f"- {missing_prop['label']}") for missing_prop in missing_properties_err]
#   print("\n")
