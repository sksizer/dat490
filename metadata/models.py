from pydantic import BaseModel
from typing import Optional


class ColumnMetadata(BaseModel):
    label: str
    section_name: str
    section_number: int
    question_number: int
    column: str  # Can be a range like "1-2" or single number
    type_of_variable: str  # "Num" or "Char"
    sas_variable_name: str
    question_prologue: Optional[str] = None
    question: str