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
    csv_name : str, optional
        The name of the CSV file. If more than one CSV is used, this arg should not be provided.
        CSV file names should be included within the data model.
    strict_typing : bool, optional
        Whether to use the types declared in the data model (True), or infer types during ingestion (False).
    """
