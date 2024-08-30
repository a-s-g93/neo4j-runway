"""
The GraphEDA Queries module contains queries that return
information about the Neo4j database and its contents.

The purpose of GraphEDA is to understand the characteristics 
of the data in graph form (nodes, relationships, and properties). 
This also helps identify errors and outliers in the data. 

The methods in this class primarily use Cypher to query and analyze 
data in the graph. The queries use Cypher because apoc.meta.schema 
uses sampling techniques and so the results are not necessarily deterministic. 

WARNING: The functions in this module can be computationally expensive.
It is not recommended to use this module on massive Neo4j databases
(i.e., nodes and relationships in the hundreds of millions) 
"""

from typing import Dict, List, Any


from ..neo4j_graph import Neo4jGraph

import logging
import neo4j 

class Queries:
    """
    The Queries module  contains queries that return
    information about the Neo4j database and its contents.

    Results are saved to a result_cache dictionary to avoid
    re-running the same queries multiple times, especially 
    queries that can be computationally expensive. 

    Attributes
    ----------
    None
    """

    def __init__(self, neo4j_graph: Neo4jGraph) -> None:
        """
        Constructor for the Queries class.

        Parameters
        ----------
        neo4j_graph : Neo4jGraph
            The Neo4jGraph object to perform the analysis on.
        """
        self.neo4j_graph = neo4j_graph
        
        # instantiate dictionariy to cache query results
        self.result_cache = dict()  
        
        # surpress some neo4j logging
        logging.getLogger("neo4j").setLevel(logging.CRITICAL) 
    
    
    def delete_cache(self) -> None:
        """
        Delete the query result cache.

        Parameters:
            None
        
        Returns:
            None
        """
        self.result_cache = dict()


    def database_indexes(self) -> List[Dict[str, Any]]:
        """
        Method to identify the Neo4j database's indexes.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary. 
            The results are a list of dictionaries, where each dictionary contains the index
            name as "name" and the list of labels for that index as "labels".
        """

        query = """SHOW INDEXES"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                self.result_cache["database_indexes"] = [record.data() for record in response]
            
        except Exception:
            self.neo4j_graph.driver.close()


    def database_constraints(self) -> List[Dict[str, Any]]:
        """
        Get the constraints for the graph database.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary. 
            The results are list of dictionaries, where each dictionary contains the  
            constraint name as "name" and the list of labels for that constraint as "labels".
        """

        query = """SHOW CONSTRAINTS"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                self.result_cache["database_constraints"] = [record.data() for record in response]
            
        except Exception:
            self.neo4j_graph.driver.close()


    # graph node count
    def node_count(self) -> int:
        """
        Count the total number of nodes in the graph.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            This result is the count of nodes in the graph. 
        """

        query = """MATCH (n) RETURN COUNT(n) AS nodeCount"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                self.result_cache["node_count"] = response_list[0]["nodeCount"]

        except Exception:
            self.neo4j_graph.driver.close()
    

    def node_label_counts(self) -> List[Dict[str, Any]]:
        """
        Count the number of nodes associated with each 
        unique label in the graph.
        
        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            The results are a list of dictionaries, where each dictionary contains 
            the unique node label in the database as "label" along with the 
            corresponding node count as "count".
        """

        query = """MATCH (n) 
                   WITH n, labels(n) AS node_labels
                   WITH node_labels[0] AS uniqueLabels
                   RETURN uniqueLabels AS label, COUNT(uniqueLabels) AS count
                   ORDER BY count DESC"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                self.result_cache["node_label_counts"] = [record.data() for record in response]
            
        except Exception:
            self.neo4j_graph.driver.close()


    def multi_label_nodes(self) -> List[Dict[str, Any]]:
        """
        Identify nodes in the graph that have multiple labels.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            The results are a list of dictionaries, where each dictionary contains 
            the node id as "node_id" and the list of labels for that node as "labels".
        """

        query = """MATCH (n) 
                   WITH n, labels(n) as node_labels
                   WHERE size(node_labels) > 1
                   WITH node_labels as labelCombinations
                   RETURN labelCombinations, count(labelCombinations) as nodeCount
                   ORDER BY nodeCount DESC"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                self.result_cache["multi_label_nodes"] = [record.data() for record in response]
            
        except Exception:
            self.neo4j_graph.driver.close()


    def node_properties(self) -> List[Dict[str, Any]]:
        """
        Get the properties for each unique node label in the graph.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            The results are a list of dictionaries, where each dictionary contains 
            the unique node label in the database as "label" along with the list of 
            properties for that label as "properties".
        """

        query = """CALL db.schema.nodeTypeProperties()"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                
                # remove the "nodeType" key from each dictionary and append to cache 
                response_list = [{k: v for k, v in record.items() if k != "nodeType"} for record in response_list]
                self.result_cache["node_properties"] = response_list
            
        except Exception:
            self.neo4j_graph.driver.close()


    def relationship_count(self) -> int:
        """
        Count the total number of relationships in the graph.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query result to the result_cache dictionary.
            This result is an integer representing the number of relationships 
            in the graph. 
        """

        query = """MATCH ()-[r]->() RETURN COUNT(r) AS relCount"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                self.result_cache["relationship_count"] = response_list[0]["relCount"]
            
        except Exception:
            self.neo4j_graph.driver.close()

    
    def relationship_type_counts(self) -> List[Dict[str, Any]]:
        """
        Count the number of relationships in the graph by 
        each unique relationship type.

        Parameters:
            None
        
        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            The results are a list of dictionaries, where each dictionary contains 
            the unique relationship type in the database as "label" along with the 
            corresponding count as "count".
        """

        query = """MATCH ()-[r]->()
                   WITH type(r) AS rel_type
                   RETURN rel_type as label, COUNT(rel_type) AS count
                   ORDER BY count DESC"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                self.result_cache["relationship_type_counts"] = [record.data() for record in response]
            
        except Exception:
            self.neo4j_graph.driver.close()


    def relationship_properties(self) -> List[Dict[str, Any]]:
        """
        Get the properties for each unique relationship type in the graph.

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the result_cache dictionary.
            The results are a of dictionaries, where each dictionary contains 
            the unique relationship property name, property data type, and whether 
            or not the relationship property is required by the schema.
        """

        query = """CALL db.schema.relTypeProperties()"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]

                # remove the "relationshipType" key from each dictionary
                response_list = [{k: v for k, v in record.items() if k != "relType"} for record in response_list]

                self.result_cache["relationship_properties"] = response_list

        except Exception:
            self.neo4j_graph.driver.close()
    

    def unlabeled_node_count(self) -> int:
        """
        Count the number of nodes in the graph that do not have labels.

        Parameters:
            None
        
        Returns:
            None
            
                The count of unlabeled nodes in the graph
        """ 

        query = """MATCH (n)
                    WHERE labels(n) = []
                    RETURN COUNT(n) AS unlabeled_ct"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                self.result_cache["unlabeled_node_count"] = response_list[0]["unlabeled_ct"]
            
        except Exception:
            self.neo4j_graph.driver.close()

    # identify unlabeled nodes
    def unlabeled_node_ids(self) -> List[Dict[str, Any]]:
        pass

    # count disconnected nodes
    def count_disconnected_nodes(self) -> List[Dict[str, Any]]:
        """
        Count the number of disconnected nodes in the graph.
        
        Parameters:
            None
        
        Returns:
            None


        - the results as a list of dictionaries, where each dictionary 
        includes a node label and the count of disconnected nodes for that label
        - ex: [{'nodeLabel': 'Customer', 'count': 2}]
        - also appends the results to the result_cache dictionary
        """

        query = """MATCH (n) 
                   WHERE NOT (n)--()
                   WITH n, labels(n) as node_labels
                   WITH node_labels[0] as nodeLabel
                   RETURN nodeLabel, count(nodeLabel) as count
                   ORDER BY count DESC"""
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query=query)
                response_list = [record.data() for record in response]
                self.result_cache["disconnected_nodes"] = response_list
                return response_list
                
        except Exception:
            self.neo4j_graph.driver.close()


    # identify disconnected nodes
    def disconnected_node_ids(self) -> List[Dict[str, Any]]:
        """
        Identify the node ids of disconnected nodes in the graph.
        Parameters:
            None
        Returns:
            list: A list of dictionaries, where each dictionary contains the node label as "nodeLabel" and
            the node id as "node_id" for each disconnected node in the graph.
            ex: [{'nodeLabel': 'Customer', 'node_id': 135}, {'nodeLabel': 'Customer', 'node_id': 170}]
        """
         
        query = """MATCH (n) 
                   WHERE NOT (n)--()
                   RETURN labels(n)[0] as nodeLabel, ID(n) as node_id"""
            
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                self.result_cache["disconnected_node_ids"] = response_list
                return response_list
            
        except Exception:
            self.neo4j_graph.driver.close()


    ############################
    # GRAPH STATISTICS FUNCTIONS
    ############################

    # node degree
    def node_degree(self) -> List[Dict[str, Any]]:
        """
        Calculate the in-degree and out-degree of each node in the graph.
        Parameters:
            None
        Returns:
            list: A list of dictionaries, where each dictionary contains the node id as "node_id",
            label as the node label, the in-degree of the node as "inDegree", and the out-degree of
            the node as "outDegree".
        """
        query = """MATCH (n)
                    OPTIONAL MATCH (n)-[r_out]->()
                    WITH n, id(n) AS nodeId, labels(n) AS nodeLabel, count(r_out) AS outDegree
                    OPTIONAL MATCH (n)<-[r_in]-()
                    RETURN nodeId, nodeLabel, count(r_in) AS inDegree, outDegree
                    ORDER BY outDegree DESC;
                    """
        
        try:
            with self.neo4j_graph.driver.session() as session:
                response = session.run(query)
                response_list = [record.data() for record in response]
                self.result_cache["node_degrees"] = response_list
                return response_list
        
        except Exception:
            self.neo4j_graph.driver.close()


    # explicit errors -- something didn't come over correctly
        
        # priority -- things in a graph created from the csv in this session
            # which things are wrong versus the designed graph
            # informative message to the user with pointers to exact issues 
            # optional -- pass the data to an LLM to interpret 
            # future -- have a method that will try to fix the issue  
        
        # future -- things in graph not created with runway
        
    
    # other possible issues