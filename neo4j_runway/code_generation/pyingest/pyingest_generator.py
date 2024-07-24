





# self._config_files_list = []
#         for item in self._cypher_map:
#             file_dict = {}
#             if self._cypher_map[item]["csv"]:
#                 file_dict["url"] = self._cypher_map[item]["csv"]
#                 file_dict["cql"] = self._cypher_map[item]["cypher"]

#                 # set globals
#                 file_dict["chunk_size"] = batch_size
#                 if field_separator:
#                     file_dict["field_separator"] = field_separator

#                 # set distict file params
#                 if self._cypher_map[item]["csv"] in pyingest_file_config:
#                     if (
#                         "batch_size"
#                         in pyingest_file_config[self._cypher_map[item]["csv"]]
#                     ):
#                         file_dict["chunk_size"] = pyingest_file_config[
#                             self._cypher_map[item]["csv"]
#                         ]["batch_size"]
#                     if (
#                         "field_separator"
#                         in pyingest_file_config[self._cypher_map[item]["csv"]]
#                     ):
#                         file_dict["field_separator"] = pyingest_file_config[
#                             self._cypher_map[item]["csv"]
#                         ]["field_separator"]
#                     if (
#                         "skip_records"
#                         in pyingest_file_config[self._cypher_map[item]["csv"]]
#                     ):
#                         file_dict["skip_records"] = pyingest_file_config[
#                             self._cypher_map[item]["csv"]
#                         ]["skip_records"]
#                     if (
#                         "skip_file"
#                         in pyingest_file_config[self._cypher_map[item]["csv"]]
#                     ):
#                         file_dict["skip_file"] = pyingest_file_config[
#                             self._cypher_map[item]["csv"]
#                         ]["skip_file"]

#                 self._config_files_list.append(file_dict)