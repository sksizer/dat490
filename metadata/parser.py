import re
from pathlib import Path
from typing import Dict
from bs4 import BeautifulSoup

try:
    # When running as a module (e.g., from notebook or parent directory)
    from .models import ColumnMetadata
except ImportError:
    # When running as a script directly
    from models import ColumnMetadata


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
        # (This check is redundant now but keeping for safety)
        if True:  # We already checked above
            try:
                # Extract fields using regex - handle non-breaking spaces
                cell_text = cell_text.replace('\xa0', ' ')  # Replace non-breaking spaces
                
                label_match = re.search(r'Label:\s*(.+?)(?=Section\s*Name:|Core\s*Section\s*Number:|$)', cell_text, re.DOTALL)
                section_name_match = re.search(r'Section\s*Name:\s*(.+?)(?=Core\s*Section\s*Number:|Section\s*Number:|$)', cell_text, re.DOTALL)
                # Handle both "Core Section Number" and "Section Number"
                section_number_match = re.search(r'(?:Core\s*)?Section\s*Number:\s*(\d+)', cell_text)
                question_number_match = re.search(r'Question\s*Number:\s*(\d+)', cell_text)
                column_match = re.search(r'Column:\s*(.+?)(?=Type\s*of\s*Variable:|$)', cell_text, re.DOTALL)
                type_match = re.search(r'Type\s*of\s*Variable:\s*(.+?)(?=SAS\s*Variable\s*Name:|$)', cell_text, re.DOTALL)
                sas_name_match = re.search(r'SAS\s*Variable\s*Name:\s*(.+?)(?=Question\s*Prologue:|Question:|$)', cell_text, re.DOTALL)
                prologue_match = re.search(r'Question\s*Prologue:\s*(.+?)(?=Question:|$)', cell_text, re.DOTALL)
                question_match = re.search(r'Question:\s*(.+?)$', cell_text, re.DOTALL)
                
                if (label_match and section_name_match and section_number_match and 
                    question_number_match and column_match and type_match and 
                    sas_name_match and question_match):
                    
                    # Clean up the extracted values
                    label = label_match.group(1).strip()
                    section_name = section_name_match.group(1).strip()
                    section_number = int(section_number_match.group(1))
                    question_number = int(question_number_match.group(1))
                    column = column_match.group(1).strip()
                    type_of_variable = type_match.group(1).strip()
                    sas_variable_name = sas_name_match.group(1).strip()
                    question_prologue = prologue_match.group(1).strip() if prologue_match else None
                    question = question_match.group(1).strip()
                    
                    # Remove any extra whitespace or newlines
                    if question_prologue and not question_prologue:
                        question_prologue = None
                    
                    # Create ColumnMetadata object
                    metadata = ColumnMetadata(
                        label=label,
                        section_name=section_name,
                        section_number=section_number,
                        question_number=question_number,
                        column=column,
                        type_of_variable=type_of_variable,
                        sas_variable_name=sas_variable_name,
                        question_prologue=question_prologue,
                        question=question
                    )
                    
                    metadata_dict[sas_variable_name] = metadata
                    
            except Exception as e:
                # Skip cells that don't parse correctly
                continue
    
    return metadata_dict

if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parent.parent
    metadata = parse_codebook_html( project_dir / Path('data/codebook_USCODE23_LLCP_021924.HTML'))
    print('finished')
