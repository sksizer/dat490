import os
import json
import logging
import pandas as pd
import subprocess
import glob

from pydantic import BaseModel
from pathlib import Path
from typing import List

from dat490.parser import ColumnMetadata, parse_codebook_html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


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
    notebook_files = glob.glob("**/*.ipynb")
    generated_files = []
    
    if not notebook_files:
        logger.info("No Jupyter notebooks found in the current directory")
        return generated_files
    
    logger.info(f"Found {len(notebook_files)} Jupyter notebooks to convert")
    
    for notebook_file in notebook_files:
        output_filename = os.path.splitext(os.path.basename(notebook_file))[0] + ".html"
        output_path = output_dir / output_filename
        
        try:
            logger.info(f"Converting {notebook_file} to HTML...")
            subprocess.run(
                ["jupyter", "nbconvert", "--to", "html", "--no-input", 
                 f"--output-dir={output_dir}", f"--output={output_filename}", notebook_file],
                check=True,
                capture_output=True
            )
            generated_files.append(str(output_path))
            logger.info(f"Successfully generated {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error converting {notebook_file}: {e}")
            logger.error(f"Command output: {e.stdout.decode()}")
            logger.error(f"Command error: {e.stderr.decode()}")
        except Exception as e:
            logger.error(f"Unexpected error converting {notebook_file}: {e}")
    
    return generated_files


if __name__ == '__main__':
    """
    Main script execution - parse BRFSS codebook and generate JSON files.
    
    This script:
    1. Loads the BRFSS data to calculate statistical information
    2. Parses the BRFSS codebook HTML file to extract column metadata and add statistics
    3. Creates a SharedModel containing all column metadata
    4. Generates two JSON files for the website application:
       - schema.json: JSON schema definition for the data model
       - model.json: The actual data model with all column metadata
    5. Converts all Jupyter notebooks to HTML for website viewing
    """
    # Use BFRSS wrapper to load data and metadata
    from dat490 import load_bfrss
    
    logger.info("Loading BRFSS data and metadata...")
    bfrss = load_bfrss(exclude_desc_columns=True)
    
    # Get metadata (this will trigger loading and parsing)
    column_metadatas = bfrss.metadata

    # Create the shared model with all column metadata
    model = SharedModel(
        columns = column_metadatas
    )
    
    # Prepare output directory
    web_data_dir = Path('website', 'content')
    web_data_dir.mkdir(parents=True, exist_ok=True)
    web_data_schem_path = web_data_dir / 'schema.json'
    web_data_path = web_data_dir / 'model.json'

    # Write JSON schema to file
    logger.info("Writing schema.json...")
    with open(web_data_schem_path, 'w') as f:
        f.write(json.dumps(model.model_json_schema(
            mode='serialization'
        )))

    # Write model data to file
    logger.info("Writing model.json...")
    with open(web_data_path, 'w') as f:
        f.write(model.model_dump_json(exclude={'columns': {'__all__': {'value_lookup'}}}))

    # Output summary of parsing results
    logger.info(f"Successfully processed {len(column_metadatas.keys())} columns from BRFSS codebook")
    
    # Convert notebooks to HTML
    logger.info("Converting Jupyter notebooks to HTML...")
    html_output_dir = Path('website', 'public', 'html', 'notebooks')
    generated_files = convert_notebooks_to_html(html_output_dir)
    
    if generated_files:
        logger.info(f"Successfully generated {len(generated_files)} HTML files:")
        for html_file in generated_files:
            logger.info(f" - {html_file}")
    else:
        logger.info("No HTML files were generated from notebooks")