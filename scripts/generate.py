import os
import json
import logging
import pandas as pd
import subprocess
import glob
import time
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Optional

from dat490.parser import ColumnMetadata, parse_codebook_html
from scripts.demographic_analysis import perform_demographic_analysis, generate_analysis_visualizations

# Demographic feature columns for analysis (26 total features)
DEMOGRAPHIC_FEATURE_COLUMNS = [
    # Demographics section columns (13 total)
    # Demographics section columns (13 total)
    'MARITAL',    # https://singular-eclair-6a5a16.netlify.app/columns/MARITAL
    'EDUCA',      # https://singular-eclair-6a5a16.netlify.app/columns/EDUCA
    'RENTHOM1',   # https://singular-eclair-6a5a16.netlify.app/columns/RENTHOM1
    'NUMHHOL4',   # https://singular-eclair-6a5a16.netlify.app/columns/NUMHHOL4
    'NUMPHON4',   # https://singular-eclair-6a5a16.netlify.app/columns/NUMPHON4
    'CPDEMO1C',   # https://singular-eclair-6a5a16.netlify.app/columns/CPDEMO1C
    'VETERAN3',   # https://singular-eclair-6a5a16.netlify.app/columns/VETERAN3
    'EMPLOY1',    # https://singular-eclair-6a5a16.netlify.app/columns/EMPLOY1
    'CHILDREN',   # https://singular-eclair-6a5a16.netlify.app/columns/CHILDREN
    'INCOME3',    # https://singular-eclair-6a5a16.netlify.app/columns/INCOME3
    'PREGNANT',   # https://singular-eclair-6a5a16.netlify.app/columns/PREGNANT
    '_HISPANC', # https://singular-eclair-6a5a16.netlify.app/columns/_HISPANC # Calculated but not sure from what
    '_CRACE1',    # https://singular-eclair-6a5a16.netlify.app/columns/_CRACE1 # Child race
    '_IMPRACE',   # https://singular-eclair-6a5a16.netlify.app/columns/_IMPRACE
    '_SEX',       # https://singular-eclair-6a5a16.netlify.app/columns/_SEX
    '_AGE80',     # https://singular-eclair-6a5a16.netlify.app/columns/_AGE80

    # Removed weight/height since there's obviously relationshp of weight to genhealth
    # 'WEIGHT2',    # https://singular-eclair-6a5a16.netlify.app/columns/WEIGHT2
    # 'HEIGHT3',    # https://singular-eclair-6a5a16.netlify.app/columns/HEIGHT3
    # 'MRACASC1',   # https://singular-eclair-6a5a16.netlify.app/columns/MRACASC1
]

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
                ["jupyter", "nbconvert", "--to", "html", "--no-input", "--allow-errors",
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
            
            # Try alternative approach: fix notebook format first
            try:
                logger.info(f"Attempting to fix notebook format for {notebook_file}...")
                import nbformat
                
                # Read and validate/fix the notebook
                with open(notebook_file, 'r') as f:
                    nb = nbformat.read(f, as_version=4)
                
                # Fix missing execution_count fields
                for cell in nb.cells:
                    if cell.cell_type == 'code' and 'execution_count' not in cell:
                        cell.execution_count = None
                
                # Write the fixed notebook to a temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as temp_file:
                    nbformat.write(nb, temp_file)
                    temp_filename = temp_file.name
                
                # Try converting the fixed notebook
                subprocess.run(
                    ["jupyter", "nbconvert", "--to", "html", "--no-input", "--allow-errors",
                     f"--output-dir={output_dir}", f"--output={output_filename}", temp_filename],
                    check=True,
                    capture_output=True
                )
                
                # Clean up temp file
                os.unlink(temp_filename)
                
                generated_files.append(str(output_path))
                logger.info(f"Successfully generated {output_path} after fixing notebook format")
                
            except Exception as fix_error:
                logger.error(f"Failed to fix and convert {notebook_file}: {fix_error}")
                
        except Exception as e:
            logger.error(f"Unexpected error converting {notebook_file}: {e}")
    
    return generated_files


def run_demographic_analysis_for_column(args):
    """
    Worker function for parallel demographic analysis.
    Each worker loads its own data to avoid memory duplication.
    
    Args:
        args: Tuple of (target_column, loading_params, min_samples)
        
    Returns:
        Tuple of (target_column, result_dict, analysis_time)
    """
    target_column, loading_params, min_samples = args
    
    start_time = time.time()
    try:
        # Each worker loads its own data to avoid memory passing
        if loading_params is None:
            # Single-threaded mode: data is passed directly (handled elsewhere)
            raise ValueError("Single-threaded mode should not use this worker function")
        else:
            # Multi-threaded mode: load data fresh in each worker
            from dat490 import load_bfrss
            bfrss = load_bfrss(exclude_desc_columns=True)
            df = bfrss.df
            metadata = bfrss.metadata
        
        result = perform_demographic_analysis(
            df=df,
            metadata=metadata,
            target_column=target_column,
            feature_columns=DEMOGRAPHIC_FEATURE_COLUMNS,
            min_samples=min_samples,
            hyperparameter_tuning=False,  # Skip for speed during bulk analysis
            logger=None  # Use default logger to avoid serialization issues
        )
        
        analysis_time = time.time() - start_time
        
        # Convert result to dictionary for serialization
        result_dict = result.model_dump()
        
        return target_column, result_dict, analysis_time
        
    except Exception as e:
        analysis_time = time.time() - start_time
        
        # Return failed result as dictionary
        failed_result_dict = {
            'target_column': target_column,
            'accuracy': 0.0,
            'classification_report': {},
            'feature_importance': [],
            'confusion_matrix': [],
            'class_labels': [],
            'model_parameters': {},
            'analysis_metadata': {},
            'successful': False,
            'error_message': str(e)
        }
        
        return target_column, failed_result_dict, analysis_time


def generate_demographic_analyses(df: pd.DataFrame, metadata: Dict[str, ColumnMetadata], 
                                output_dir: Path, min_samples: int = 1000,
                                max_workers: int = 4, sequential: bool = False) -> Dict[str, float]:
    """
    Generate demographic analyses for all applicable columns.
    
    Args:
        df: BRFSS DataFrame
        metadata: Column metadata dictionary
        output_dir: Directory to save analysis results
        min_samples: Minimum sample size for analysis
        max_workers: Number of parallel workers
        
    Returns:
        Dictionary mapping column names to accuracy scores
    """
    analysis_start_time = time.time()
    
    # Identify candidate columns for analysis
    candidate_columns = []
    
    for col_name, col_meta in metadata.items():
        if col_name not in df.columns:
            continue
            
        # Skip if this is a demographic feature column (don't analyze predictors)
        if col_name in DEMOGRAPHIC_FEATURE_COLUMNS:
            continue
            
        # Check if column has enough valid data
        valid_count = df[col_name].dropna().shape[0]
        if valid_count < min_samples:
            continue
            
        # Skip categorical columns that are too sparse (>50% categories)
        unique_values = df[col_name].dropna().nunique()
        if unique_values > valid_count * 0.5:
            continue
            
        # Skip columns with too few categories for classification (need at least 2)
        if unique_values < 2:
            continue
            
        candidate_columns.append(col_name)
    
    logger.info(f"Identified {len(candidate_columns)} candidate columns for demographic analysis")
    logger.info(f"Analysis criteria: min_samples={min_samples}, excluding {len(DEMOGRAPHIC_FEATURE_COLUMNS)} demographic features")
    
    if len(candidate_columns) == 0:
        logger.warning("No candidate columns found for demographic analysis")
        return {}
    
    # Prepare arguments for processing
    if sequential or max_workers == 1:
        # Single-threaded: we'll handle this separately (no worker function needed)
        analysis_args = None
    else:
        # Multi-threaded: each worker will load its own data
        # We just pass loading parameters (which are minimal)
        loading_params = {'exclude_desc_columns': True}  # Parameters for load_bfrss()
        analysis_args = [
            (col, loading_params, min_samples) 
            for col in candidate_columns
        ]
    
    results = {}
    successful_analyses = 0
    total_analysis_time = 0
    
    if sequential or max_workers == 1 or len(candidate_columns) <= 5:
        # Run sequentially for debugging or small datasets
        logger.info(f"Starting sequential demographic analysis...")
        
        for i, target_column in enumerate(candidate_columns, 1):
            start_time = time.time()
            
            try:
                result = perform_demographic_analysis(
                    df=df,
                    metadata=metadata,
                    target_column=target_column,
                    feature_columns=DEMOGRAPHIC_FEATURE_COLUMNS,
                    min_samples=min_samples,
                    hyperparameter_tuning=False,
                    logger=logger
                )
                
                analysis_time = time.time() - start_time
                total_analysis_time += analysis_time
                
                if result.successful:
                    successful_analyses += 1
                    results[target_column] = result.accuracy
                    
                    # Save individual analysis results
                    analysis_file = output_dir / f"{target_column}_demographic_analysis.json"
                    with open(analysis_file, 'w') as f:
                        f.write(result.model_dump_json(indent=2))
                    
                    # Generate visualizations
                    viz_dir = Path('website/public/images')
                    viz_files = generate_analysis_visualizations(
                        result=result,
                        output_dir=viz_dir,
                        format='svg'
                    )
                    
                    logger.info(f"[{i:3d}/{len(candidate_columns)}] {target_column}: accuracy={result.accuracy:.3f}, time={analysis_time:.1f}s")
                    
                else:
                    logger.warning(f"[{i:3d}/{len(candidate_columns)}] {target_column}: FAILED - {result.error_message}")
                    
            except Exception as e:
                analysis_time = time.time() - start_time
                total_analysis_time += analysis_time
                logger.error(f"[{i:3d}/{len(candidate_columns)}] {target_column}: ERROR - {str(e)}")
    
    else:
        # Run analyses in parallel - each worker loads its own data
        logger.info(f"Starting parallel demographic analysis with {max_workers} workers...")
        logger.info(f"Each worker will load its own copy of the data to avoid memory issues")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_column = {
                executor.submit(run_demographic_analysis_for_column, args): args[0] 
                for args in analysis_args
            }
            
            # Process completed analyses
            for i, future in enumerate(as_completed(future_to_column), 1):
                column_name = future_to_column[future]
                
                try:
                    target_column, result_dict, analysis_time = future.result()
                    total_analysis_time += analysis_time
                    
                    if result_dict['successful']:
                        successful_analyses += 1
                        results[target_column] = result_dict['accuracy']
                        
                        # Save individual analysis results
                        analysis_file = output_dir / f"{target_column}_demographic_analysis.json"
                        with open(analysis_file, 'w') as f:
                            json.dump(result_dict, f, indent=2)
                        
                        # Generate visualizations
                        from scripts.demographic_analysis import DemographicAnalysisResult
                        result_obj = DemographicAnalysisResult(**result_dict)
                        
                        viz_dir = Path('website/public/images')
                        viz_files = generate_analysis_visualizations(
                            result=result_obj,
                            output_dir=viz_dir,
                            format='svg'
                        )
                        
                        logger.info(f"[{i:3d}/{len(candidate_columns)}] {target_column}: accuracy={result_dict['accuracy']:.3f}, time={analysis_time:.1f}s")
                        
                    else:
                        logger.warning(f"[{i:3d}/{len(candidate_columns)}] {target_column}: FAILED - {result_dict['error_message']}")
                        
                except Exception as e:
                    logger.error(f"[{i:3d}/{len(candidate_columns)}] {column_name}: ERROR - {str(e)}")
    
    # Summary statistics
    total_time = time.time() - analysis_start_time
    avg_analysis_time = total_analysis_time / len(candidate_columns) if candidate_columns else 0
    
    logger.info(f"Demographic analysis completed:")
    logger.info(f"  Successful analyses: {successful_analyses}/{len(candidate_columns)} ({successful_analyses/len(candidate_columns)*100:.1f}%)")
    logger.info(f"  Total time: {total_time:.1f}s")
    logger.info(f"  Analysis time: {total_analysis_time:.1f}s")
    logger.info(f"  Average per column: {avg_analysis_time:.1f}s")
    logger.info(f"  Parallel efficiency: {total_analysis_time/total_time:.1f}x")
    
    return results


def update_metadata_with_analysis_scores(metadata: Dict[str, ColumnMetadata], 
                                        analysis_scores: Dict[str, float]) -> Dict[str, ColumnMetadata]:
    """
    Update column metadata with demographic analysis scores.
    
    Args:
        metadata: Column metadata dictionary
        analysis_scores: Dictionary mapping column names to accuracy scores
        
    Returns:
        Updated metadata dictionary
    """
    updated_metadata = metadata.copy()
    
    for col_name, score in analysis_scores.items():
        if col_name in updated_metadata:
            updated_metadata[col_name].demographic_analysis_score = score
            
    logger.info(f"Updated {len(analysis_scores)} columns with demographic analysis scores")
    
    return updated_metadata


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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate BRFSS metadata and analysis files')
    parser.add_argument('--demographic-analysis', action='store_true', 
                       help='Generate demographic analysis for applicable columns')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with limited columns (GENHLTH, ASTHMS1, MICHD)')
    parser.add_argument('--sequential', action='store_true',
                       help='Run analysis sequentially instead of in parallel')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum number of parallel workers (default: 4)')
    
    args = parser.parse_args()
    
    # Use BFRSS wrapper to load data and metadata
    from dat490 import load_bfrss
    
    logger.info("Loading BRFSS data and metadata...")
    bfrss = load_bfrss(exclude_desc_columns=True)
    
    # Get metadata (this will trigger loading and parsing)
    column_metadatas = bfrss.metadata
    
    # Run demographic analysis if requested
    demographic_analysis_enabled = args.demographic_analysis
    
    if demographic_analysis_enabled:
        logger.info("Starting demographic analysis generation...")
        
        # Generate demographic analyses for all applicable columns
        web_content_dir = Path('website', 'content')
        web_content_dir.mkdir(parents=True, exist_ok=True)
        
        if args.test_mode:
            # Test with just a few known good columns
            test_columns = ['GENHLTH', 'ASTHMS1', 'MICHD']
            test_metadata = {col: meta for col, meta in column_metadatas.items() if col in test_columns}
            logger.info(f"Test mode: analyzing {len(test_columns)} columns: {test_columns}")
            
            analysis_scores = generate_demographic_analyses(
                df=bfrss.df,
                metadata=test_metadata,
                output_dir=web_content_dir,
                min_samples=1000,
                max_workers=min(2, args.max_workers),
                sequential=args.sequential or True  # Default to sequential in test mode
            )
        else:
            # Full analysis
            analysis_scores = generate_demographic_analyses(
                df=bfrss.df,
                metadata=column_metadatas,
                output_dir=web_content_dir,
                min_samples=1000,
                max_workers=args.max_workers,
                sequential=args.sequential
            )
        
        # Update metadata with analysis scores
        column_metadatas = update_metadata_with_analysis_scores(
            metadata=column_metadatas,
            analysis_scores=analysis_scores
        )
    else:
        logger.info("Demographic analysis disabled (use --demographic-analysis to enable)")

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