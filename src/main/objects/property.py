from typing import List, Dict, Union, Any

from pydantic import BaseModel


class Property(BaseModel):
    """
    Property representation.
    """

    name: str
    csv_mapping: str
    is_unique: bool

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        pass

    
