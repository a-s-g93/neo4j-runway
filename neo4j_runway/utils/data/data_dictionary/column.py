from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from ....resources.mappings.type_mappings import PythonTypeEnum


class Column(BaseModel, use_enum_values=True):
    """
    A column representation in a relational table.

    Attributes
    ----------
    name : str
        The column name.
    description : Optional[str], optional
        The column description, by default None
    primary_key : bool, optional
        Whether column is a primary key, by default False
    foreign_key : bool, optional
        Whether column is a foreign key, by default False
    key : bool, optional
        Whether column is a key of any type, by default False
    aliases : Optional[List[str]], optional
        Any other columns across the tables that could also map to the data in this column, by default None
    python_type: Optional[str], optional
        The Python type of the column, by default None
    ignore : bool, optional
        Whether to ignore this column in data modeling, by default False
    nullable : bool, optional
        Whether this column is nullable, by default True
    """

    name: str
    description: Optional[str] = None
    primary_key: bool = False
    foreign_key: bool = False
    key: bool = False
    aliases: Optional[List[str]] = None
    python_type: Optional[PythonTypeEnum] = None
    ignore: bool = False
    nullable: bool = True

    @field_validator("aliases")
    def validate_aliases(
        cls, aliases: Optional[List[str]], info: ValidationInfo
    ) -> Optional[List[str]]:
        if aliases is not None and info.context is not None:
            column_names = info.context.get("column_names")
            if column_names is not None:
                invalid_aliases = list()
                for alias in aliases:
                    if alias not in column_names:
                        invalid_aliases.append(alias)
                if len(invalid_aliases) > 0:
                    raise ValueError(
                        f"{invalid_aliases} are not valid column names in the provided data dictionary."
                    )
        return aliases

    @model_validator(mode="after")
    def validate_model(self) -> "Column":
        if self.primary_key:
            self.nullable = False
            self.key = True
        elif self.foreign_key:
            self.key = True
        if self.primary_key and self.foreign_key:
            raise ValueError("`primary_key` and `foreign_key` may not both be True.")
        return self

    @property
    def compact_dict(self) -> Dict[str, str]:
        """
        Compact representation of the column information.

        Returns
        -------
        Dict[str, str]
            A dictionary.
        """

        compact_info: str = (
            (self.description if self.description is not None else "")
            + (
                (" Has aliases: " + str(self.aliases))
                if self.aliases is not None
                else ""
            )
            + (" | ignore" if self.ignore else "")
        )

        return {self.name: compact_info}
