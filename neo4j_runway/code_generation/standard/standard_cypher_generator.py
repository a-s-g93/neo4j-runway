"""
This file contains the code to generate regular Cypher code.
"""

import os
from typing import Any, Dict, List, Optional, Union

import yaml


from ..base import BaseCodeGenerator
from ...models.core import DataModel

class StandardCypherCodeGenerator(BaseCodeGenerator):
    """
    A class for generating standard plain old Cypher code.
    """
