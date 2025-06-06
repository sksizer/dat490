import os
import json
import pandas as pd
import subprocess
import glob

from pydantic import BaseModel
from pathlib import Path
from typing import List

from parser import ColumnMetadata, parse_codebook_html


class SharedModel(BaseModel):
    """Container model for all column metadata to be exported as JSON."""
    columns: dict[str, ColumnMetadata]  # Map of SAS variable names to column metadata


def convert_notebooks_to_html(output_dir: Path) -> List[str]:
    """
    Converts all Jupyter notebooks in the current directory to HTML and saves them to the specified output directory.
    
    Args:
        output_dir: Path to the directory where HTML files will be saved
        
    Returns:
        List of paths to the generated HTML files
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all notebook files
    notebook_files = glob.glob("*.ipynb")
    generated_files = []
    
    if not notebook_files:
        print("No Jupyter notebooks found in the current directory")
        return generated_files
    
    print(f"Found {len(notebook_files)} Jupyter notebooks to convert")
    
    for notebook_file in notebook_files:
        output_filename = os.path.splitext(os.path.basename(notebook_file))[0] + ".html"
        output_path = output_dir / output_filename
        
        try:
            print(f"Converting {notebook_file} to HTML...")
            subprocess.run(
                ["jupyter", "nbconvert", "--to", "html", "--no-input", 
                 f"--output={output_path}", notebook_file],
                check=True,
                capture_output=True
            )
            generated_files.append(str(output_path))
            print(f"Successfully generated {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {notebook_file}: {e}")
            print(f"Command output: {e.stdout.decode()}")
            print(f"Command error: {e.stderr.decode()}")
        except Exception as e:
            print(f"Unexpected error converting {notebook_file}: {e}")
    
    return generated_files


if __name__ == '__main__':
    """
    Main script execution - parse BRFSS codebook and generate JSON files.
    
    This script:
    1. Loads the BRFSS data to calculate statistical information
    2. Parses the BRFSS codebook HTML file to extract column metadata and add statistics
    3. Creates a SharedModel containing all column metadata
    4. Generates two JSON files for the web application:
       - schema.json: JSON schema definition for the data model
       - model.json: The actual data model with all column metadata
    5. Converts all Jupyter notebooks to HTML for web viewing
    """
    # Load the BRFSS data
    try:
        print("Loading BRFSS data...")
        df = pd.read_parquet(Path('data', 'LLCP2023.parquet'))
        print(f"Loaded data with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Continuing without statistical information")
        df = None
    
    # Parse the codebook HTML file with data for statistics
    print("Parsing codebook and calculating statistics...")
    column_metadatas = parse_codebook_html(
        Path('data', 'codebook_USCODE23_LLCP_021924.HTML'),
        df
    )

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
    print("Writing schema.json...")
    with open(web_data_schem_path, 'w') as f:
        f.write(json.dumps(model.model_json_schema(
            mode='serialization'
        )))

    # Write model data to file
    print("Writing model.json...")
    with open(web_data_path, 'w') as f:
        f.write(model.model_dump_json())

    # Output summary of parsing results
    print(f"Successfully processed {len(column_metadatas.keys())} columns from BRFSS codebook")
    
    # Convert notebooks to HTML
    print("\nConverting Jupyter notebooks to HTML...")
    html_output_dir = Path('web', 'public', 'html', 'notebooks')
    generated_files = convert_notebooks_to_html(html_output_dir)
    
    if generated_files:
        print(f"\nSuccessfully generated {len(generated_files)} HTML files:")
        for html_file in generated_files:
            print(f" - {html_file}")
    else:
        print("No HTML files were generated from notebooks")