#!/usr/bin/env python3
"""
Script to examine column names in parquet files to understand X prefix issue
"""

import pandas as pd
import sys
from pathlib import Path

def examine_parquet_columns():
    # Define file paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    files = [
        "LLCP2023.parquet",
        "LLCP2023_desc.parquet", 
        "LLCP2023_desc_categorized.parquet"
    ]
    
    file_paths = [data_dir / f for f in files]
    
    # Check if files exist
    for file_path in file_paths:
        if not file_path.exists():
            print(f"Error: {file_path} does not exist")
            return False
    
    print("Examining column names in parquet files...\n")
    
    # Read column names from each file
    file_columns = {}
    for i, file_path in enumerate(file_paths):
        try:
            df = pd.read_parquet(file_path)
            file_columns[files[i]] = list(df.columns)
            print(f"{files[i]}:")
            print(f"  Total columns: {len(df.columns)}")
            
            # Check for columns starting with X
            x_columns = [col for col in df.columns if col.startswith('X')]
            if x_columns:
                print(f"  Columns starting with 'X': {len(x_columns)}")
                print(f"  First 10 X columns: {x_columns[:10]}")
            else:
                print(f"  No columns starting with 'X'")
                
            # Check for columns starting with underscore
            underscore_columns = [col for col in df.columns if col.startswith('_')]
            if underscore_columns:
                print(f"  Columns starting with '_': {len(underscore_columns)}")
                print(f"  First 10 _ columns: {underscore_columns[:10]}")
            else:
                print(f"  No columns starting with '_'")
            
            print()
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
    
    # Compare columns between reference file and other files
    reference_file = files[0]  # LLCP2023.parquet
    reference_columns = set(file_columns[reference_file])
    
    print(f"\nComparing columns with reference file ({reference_file}):\n")
    
    for i in range(1, len(files)):
        current_file = files[i]
        current_columns = set(file_columns[current_file])
        
        print(f"{current_file} vs {reference_file}:")
        
        # Find columns in current file but not in reference
        extra_columns = current_columns - reference_columns
        if extra_columns:
            print(f"  Columns in {current_file} but not in {reference_file}: {len(extra_columns)}")
            x_extra = [col for col in extra_columns if col.startswith('X')]
            if x_extra:
                print(f"  Extra X columns: {len(x_extra)}")
                print(f"  First 10 extra X columns: {x_extra[:10]}")
        
        # Find columns in reference but not in current
        missing_columns = reference_columns - current_columns
        if missing_columns:
            print(f"  Columns in {reference_file} but not in {current_file}: {len(missing_columns)}")
            underscore_missing = [col for col in missing_columns if col.startswith('_')]
            if underscore_missing:
                print(f"  Missing _ columns: {len(underscore_missing)}")
                print(f"  First 10 missing _ columns: {underscore_missing[:10]}")
        
        print()
    
    # Look for potential X->_ mappings
    print("Analyzing potential X->_ mappings:\n")
    
    for i in range(1, len(files)):
        current_file = files[i]
        current_columns = set(file_columns[current_file])
        
        print(f"Potential mappings for {current_file}:")
        
        x_columns = [col for col in current_columns if col.startswith('X_')]
        potential_mappings = []
        
        for x_col in x_columns:
            # Remove X prefix to get potential original name
            potential_original = x_col[1:]  # Remove 'X'
            if potential_original in reference_columns:
                potential_mappings.append((x_col, potential_original))
        
        if potential_mappings:
            print(f"  Found {len(potential_mappings)} potential X->_ mappings")
            print(f"  First 10 mappings: {potential_mappings[:10]}")
        else:
            print(f"  No clear X->_ mappings found")
        
        print()
    
    return True

if __name__ == "__main__":
    examine_parquet_columns()