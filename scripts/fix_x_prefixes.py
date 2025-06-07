#!/usr/bin/env python3
"""
Script to fix X prefixes in parquet files by renaming X_ columns back to _ columns
"""

import pandas as pd
import sys
from pathlib import Path
import shutil

def fix_x_prefixes():
    # Define file paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    # Reference file (correct column names)
    reference_file = data_dir / "LLCP2023.parquet"
    
    # Files to fix
    files_to_fix = [
        "LLCP2023_desc.parquet",
        "LLCP2023_desc_categorized.parquet"
    ]
    
    # Check if reference file exists
    if not reference_file.exists():
        print(f"Error: Reference file {reference_file} does not exist")
        return False
    
    print("Starting X prefix fix process...\n")
    
    # Read reference file to get correct column names
    try:
        reference_df = pd.read_parquet(reference_file)
        reference_columns = set(reference_df.columns)
        reference_underscore_columns = [col for col in reference_columns if col.startswith('_')]
        print(f"Reference file has {len(reference_underscore_columns)} columns starting with '_'")
        print(f"Total reference columns: {len(reference_columns)}")
    except Exception as e:
        print(f"Error reading reference file: {e}")
        return False
    
    # Process each file that needs fixing
    for file_name in files_to_fix:
        file_path = data_dir / file_name
        
        if not file_path.exists():
            print(f"Warning: {file_path} does not exist, skipping...")
            continue
            
        print(f"\nProcessing {file_name}...")
        
        try:
            # Read the file
            df = pd.read_parquet(file_path)
            original_columns = list(df.columns)
            
            print(f"  Original columns: {len(original_columns)}")
            
            # Find X columns that should be renamed to _ columns
            x_columns = [col for col in df.columns if col.startswith('X_')]
            print(f"  Columns starting with 'X_': {len(x_columns)}")
            
            # Create mapping of X columns to _ columns
            rename_mapping = {}
            for x_col in x_columns:
                potential_underscore_col = x_col[1:]  # Remove 'X' to get '_...'
                if potential_underscore_col in reference_columns:
                    rename_mapping[x_col] = potential_underscore_col
            
            print(f"  Columns to rename: {len(rename_mapping)}")
            
            if rename_mapping:
                print(f"  First 10 renames: {list(rename_mapping.items())[:10]}")
                
                # Create backup
                backup_path = file_path.with_suffix('.parquet.backup')
                print(f"  Creating backup: {backup_path}")
                shutil.copy2(file_path, backup_path)
                
                # Apply renames
                df_renamed = df.rename(columns=rename_mapping)
                
                # Verify the renames worked
                new_columns = list(df_renamed.columns)
                renamed_underscore_columns = [col for col in new_columns if col.startswith('_')]
                
                print(f"  After rename - columns starting with '_': {len(renamed_underscore_columns)}")
                print(f"  After rename - total columns: {len(new_columns)}")
                
                # Save the corrected file
                print(f"  Saving corrected file...")
                df_renamed.to_parquet(file_path, index=False)
                
                print(f"  ✓ Successfully fixed {file_name}")
                print(f"    - Renamed {len(rename_mapping)} columns")
                print(f"    - Backup saved as {backup_path.name}")
                
            else:
                print(f"  No columns to rename in {file_name}")
                
        except Exception as e:
            print(f"  Error processing {file_name}: {e}")
            return False
    
    print(f"\nX prefix fix process completed!")
    return True

def verify_fixes():
    """Verify that the fixes were applied correctly"""
    print(f"\nVerifying fixes...")
    
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    # Reference file
    reference_file = data_dir / "LLCP2023.parquet"
    
    # Fixed files
    fixed_files = [
        "LLCP2023_desc.parquet",
        "LLCP2023_desc_categorized.parquet"
    ]
    
    try:
        reference_df = pd.read_parquet(reference_file)
        reference_underscore_columns = set([col for col in reference_df.columns if col.startswith('_')])
        
        print(f"Reference file _ columns: {len(reference_underscore_columns)}")
        
        for file_name in fixed_files:
            file_path = data_dir / file_name
            if file_path.exists():
                df = pd.read_parquet(file_path)
                underscore_columns = set([col for col in df.columns if col.startswith('_')])
                x_columns = [col for col in df.columns if col.startswith('X_')]
                
                print(f"{file_name}:")
                print(f"  _ columns: {len(underscore_columns)}")
                print(f"  X_ columns: {len(x_columns)}")
                
                # Check if all reference _ columns are present
                missing_underscore = reference_underscore_columns - underscore_columns
                if missing_underscore:
                    print(f"  Missing _ columns: {len(missing_underscore)}")
                else:
                    print(f"  ✓ All reference _ columns present")
                    
        print(f"Verification completed!")
        
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    success = fix_x_prefixes()
    if success:
        verify_fixes()
    else:
        print("Fix process failed!")
        sys.exit(1)