"""
This file contains the code to generate regular Cypher code.
"""

from ..base import BaseCodeGenerator


class StandardCypherCodeGenerator(BaseCodeGenerator):
    """
    A class for generating standard plain old Cypher code.

    Attributes
    ----------
    data_model : DataModel
        The data model to base ingestion code on.
    file_directory : str, optional
        Where the files are located.
    file_output_directory : str, optional
        The location that generated files should be saved to.
    source_name : str, optional
        The name of the data file. If more than one file is used, this arg should not be provided.
        File names should be included within the data model. By default = ""
    strict_typing : bool, optional
        Whether to use the types declared in the data model (True), or infer types during ingestion (False).
    """
