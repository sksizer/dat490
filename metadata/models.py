from pydantic import BaseModel, Field
from typing import Optional

class ColumnMetadata(BaseModel):
    label: str
    sas_variable_name: str
    section_name: Optional[str] = None
    section_number: Optional[int] = None
    question_number: Optional[int] = None
    column: Optional[str] = None  # Can be a range like "1-2" or single number
    type_of_variable: Optional[str] = None  # "Num" or "Char"
    question_prologue: Optional[str] = None
    question: Optional[str] = None
    value_lookup: dict[None | int, str] # This is a dictionary that returns the textual