import os
import json

from pydantic import BaseModel, Field
from typing import Optional
import re
from pathlib import Path
from typing import Dict
from bs4 import BeautifulSoup, PageElement


class ValueDef(BaseModel):
    description: str


class ValueRange(ValueDef):
    start: int
    end: int


class ColumnMetadata(BaseModel):
    computed: bool
    label: str
    sas_variable_name: str
    section_name: Optional[str] = None
    section_number: Optional[int] = None
    module_number: Optional[int] = None  # Added module_number field
    question_number: Optional[int] = None
    column: Optional[str] = None  # Can be a range like "1-2" or single number
    type_of_variable: Optional[str] = None  # "Num" or "Char".first().name
    question_prologue: Optional[str] = None
    question: Optional[str] = None
    value_lookup: list[ValueDef]
    html_name: str


class SharedModel(BaseModel):
    columns:  dict[str, ColumnMetadata]


def get_value_def(tr:PageElement) -> ValueDef | ValueRange:
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

def get_value_lookup(table:PageElement) -> list[ValueRange]:
    """
    Given one of the branch table objects, we can extract out in a fairly
    simple manner all the possible values for the target column

    Simplified table structure example:
    <table>
    <tbody>
    <tr>
    <td>value</td> (which might be a single int value, blank or could be a range
    <td>Value description
    </tr>
    </tbody>
    </table>

    :param table:
    :return:
    """
    value_ranges : list[ValueRange] = []

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
    column_metadatas = parse_codebook_html(Path('data', 'codebook_USCODE23_LLCP_021924.HTML'))

    trimmed_metadatas = {}

    for key,value in column_metadatas.items():
        trimmed_metadatas[key] = ColumnMetadata(
            **value.model_dump(exclude={'value_lookup'})
        )

    model = SharedModel(
        columns = trimmed_metadatas
    )
    # Write out data
    web_data_dir = Path('web', 'content')
    web_data_dir.mkdir(parents=True, exist_ok=True)
    web_data_schem_path = web_data_dir / 'schema.json'
    web_data_path = web_data_dir / 'model.json'

    with open(web_data_schem_path, 'w') as f:
        f.write(json.dumps(model.model_json_schema(
            mode='serialization'
        )))

    with open(web_data_path, 'w') as f:
        f.write(model.model_dump_json())

    print(len(column_metadatas.keys()))