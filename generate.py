import os
import json

from pydantic import BaseModel, Field
from typing import Optional
import re
from pathlib import Path
from typing import Dict
from bs4 import BeautifulSoup, PageElement


class ValueDef(BaseModel):
    """Base model for representing value definitions in BRFSS survey data."""
    description: str


class ValueRange(ValueDef):
    """Model for value definitions that have a numeric range (single value or range of values)."""
    start: int
    end: int


class ColumnMetadata(BaseModel):
    """
    Model representing metadata for a single column in the BRFSS dataset.
    Contains information parsed from the codebook including variable details,
    associated question text, and possible values.
    """
    computed: bool                      # Whether this is a calculated/derived variable
    label: str                          # Human-readable label for the variable
    sas_variable_name: str              # Original SAS variable name from dataset
    section_name: Optional[str] = None  # Name of the survey section
    section_number: Optional[int] = None # Core section number
    module_number: Optional[int] = None # Module number for optional modules
    question_number: Optional[int] = None # Question number within section
    column: Optional[str] = None        # Column position in dataset (can be range like "1-2")
    type_of_variable: Optional[str] = None # "Num" or "Char"
    question_prologue: Optional[str] = None # Text before the actual question
    question: Optional[str] = None      # The actual question text from survey
    value_lookup: list[ValueDef]        # Possible values for this variable
    html_name: str                      # HTML anchor name for linking to codebook


class SharedModel(BaseModel):
    """Container model for all column metadata to be exported as JSON."""
    columns: dict[str, ColumnMetadata]  # Map of SAS variable names to column metadata


def get_value_def(tr:PageElement) -> ValueDef | ValueRange:
    """
    Extract value definition from a table row in the codebook.
    
    Parses a table row containing value codes and their descriptions. Handles both
    single values and ranges (e.g., "1-30").
    
    Args:
        tr: BeautifulSoup PageElement representing a table row with value information
        
    Returns:
        Either a ValueDef (for non-numeric or unparseable values) or
        ValueRange (for single numbers or numeric ranges)
    """
    cells = tr.find_all('td')

    value_text = cells[0].text.strip()
    description = cells[1].text.strip()

    # Check if the value is actually a range such as "1 - 30" or "1-30"
    range_match = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', value_text)
    if range_match:
        return ValueRange(
            start = int(range_match.group(1)),
            end = int(range_match.group(2)),
            description=description
        )
    else:
        # Try to parse as single integer
        try:
            return ValueRange(
                start = int(value_text),
                end = int(value_text),
                description=description)
        except:
            return ValueDef(
                description=description
            )

def get_value_lookup(table:PageElement) -> list[ValueDef]:
    """
    Extract all possible values for a column from a codebook table.
    
    Given a table from the codebook HTML, extracts all value definitions
    (codes and their descriptions) from the rows.
    
    Args:
        table: BeautifulSoup PageElement representing a table containing value codes
              and descriptions
    
    Returns:
        List of ValueDef/ValueRange objects containing all possible values
        for the column
    
    Example table structure:
    <table>
    <tbody>
    <tr>
        <td>value</td> <!-- single int value, blank, or range like "1-30" -->
        <td>Value description</td>
    </tr>
    </tbody>
    </table>
    """
    value_ranges : list[ValueDef] = []

    for tr in table.find('tbody').find_all('tr'):
        value_ranges.append(get_value_def(tr))

    return value_ranges

def parse_codebook_html(html_path: Path) -> Dict[str, ColumnMetadata]:
    """
    Parse the BRFSS codebook HTML file and extract column metadata.

    Args:
        html_path: Path to the HTML codebook file

    Returns:
        Dictionary mapping SAS variable names to ColumnMetadata objects
    """
    with open(html_path, 'r', encoding='windows-1252') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all div elements with class "branch"
    branches = soup.find_all('div', class_='branch')


    # The first one is the Codebook header table which we don't want
    branches = branches[1:]

    metadata_dict = {}

    for branch in branches:
        html_name = branch.find('a')['name']
        print('html_name' + html_name)
        # Find the table with summary="Procedure Report: Report"
        table = branch.find('table', attrs={'summary': 'Procedure Report: Report'})
        if not table:
            continue

        # Find the first td in the thead > tr
        thead = table.find('thead')
        if not thead:
            continue

        first_tr = thead.find('tr')
        if not first_tr:
            continue

        # Find td with metadata content - may not have all classes
        metadata_cell = None
        for td in first_tr.find_all('td'):
            text = td.get_text()
            if text:
                # Clean text before checking
                text_clean = text.replace('\xa0', ' ')
                if 'Label:' in text_clean and 'SAS Variable Name:' in text_clean:
                    metadata_cell = td
                    break

        if not metadata_cell:
            continue

        cell_text = metadata_cell.get_text()

        # Check if this cell contains column metadata by looking for key fields
        try:
            # Extract fields using regex - handle non-breaking spaces
            cell_text = cell_text.replace('\xa0', ' ')  # Replace non-breaking spaces

            label_match = re.search(r'Label:\s*(.+?)(?=Section\s*Name:|Core\s*Section\s*Number:|Module\s*Number:|$)', cell_text, re.DOTALL)
            section_name_match = re.search(r'Section\s*Name:\s*(.+?)(?=Core\s*Section\s*Number:|Section\s*Number:|Module\s*Number:|Question\s*Number:|$)', cell_text, re.DOTALL)
            # Handle both "Core Section Number" and "Section Number"
            section_number_match = re.search(r'(?:Core\s*)?Section\s*Number:\s*(\d+)', cell_text)
            # Handle "Module Number"
            module_number_match = re.search(r'Module\s*Number:\s*(\d+)', cell_text)
            question_number_match = re.search(r'Question\s*Number:\s*(\d+)', cell_text)
            column_match = re.search(r'Column:\s*(.+?)(?=Type\s*of\s*Variable:|$)', cell_text, re.DOTALL)
            type_match = re.search(r'Type\s*of\s*Variable:\s*(.+?)(?=SAS\s*Variable\s*Name:|$)', cell_text, re.DOTALL)
            sas_name_match = re.search(r'SAS\s*Variable\s*Name:\s*(.+?)(?=Question\s*Prologue:|Question:|$)', cell_text, re.DOTALL)
            prologue_match = re.search(r'Question\s*Prologue:\s*(.+?)(?=Question:|$)', cell_text, re.DOTALL)
            question_match = re.search(r'Question:\s*(.+?)$', cell_text, re.DOTALL)

            # Only require label and SAS variable name
            if label_match and sas_name_match:

                # Clean up the extracted values
                label = label_match.group(1).strip()
                sas_variable_name = sas_name_match.group(1).strip()

                # Extract optional fields
                section_name = section_name_match.group(1).strip() if section_name_match else None
                section_number = int(section_number_match.group(1)) if section_number_match else None
                module_number = int(module_number_match.group(1)) if module_number_match else None
                question_number = int(question_number_match.group(1)) if question_number_match else None
                column = column_match.group(1).strip() if column_match else None
                type_of_variable = type_match.group(1).strip() if type_match else None
                question_prologue = prologue_match.group(1).strip() if prologue_match else None
                question = question_match.group(1).strip() if question_match else None

                # Remove any extra whitespace or newlines
                if question_prologue and not question_prologue:
                    question_prologue = None

                # Create ColumnMetadata object
                metadata = ColumnMetadata(
                    label=label,
                    sas_variable_name=sas_variable_name,
                    section_name=section_name,
                    section_number=section_number,
                    module_number=module_number,
                    question_number=question_number,
                    column=column,
                    type_of_variable=type_of_variable,
                    question_prologue=question_prologue,
                    question=question,
                    value_lookup=get_value_lookup(table),
                    computed= True if section_name == 'Calculated Variables' or section_name == 'Calculated Race Variables' else False,
                    html_name=html_name
                )

                metadata_dict[sas_variable_name] = metadata

        except Exception as e:
            # Skip cells that don't parse correctly but show problems
            print(e)

    return metadata_dict


if __name__ == '__main__':
    """
    Main script execution - parse BRFSS codebook and generate JSON files.
    
    This script:
    1. Parses the BRFSS codebook HTML file to extract column metadata
    2. Creates a SharedModel containing all column metadata
    3. Generates two JSON files for the web application:
       - schema.json: JSON schema definition for the data model
       - model.json: The actual data model with all column metadata
    """
    # Parse the codebook HTML file
    column_metadatas = parse_codebook_html(Path('data', 'codebook_USCODE23_LLCP_021924.HTML'))

    # Create the shared model with all column metadata
    model = SharedModel(
        columns = column_metadatas
    )
    
    # Prepare output directory
    web_data_dir = Path('web', 'content')
    web_data_dir.mkdir(parents=True, exist_ok=True)
    web_data_schem_path = web_data_dir / 'schema.json'
    web_data_path = web_data_dir / 'model.json'

    # Write JSON schema to file
    with open(web_data_schem_path, 'w') as f:
        f.write(json.dumps(model.model_json_schema(
            mode='serialization'
        )))

    # Write model data to file
    with open(web_data_path, 'w') as f:
        f.write(model.model_dump_json())

    # Output summary of parsing results
    print(f"Successfully processed {len(column_metadatas.keys())} columns from BRFSS codebook")