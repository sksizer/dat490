#!/usr/bin/env python3
"""
Test script to check if parquet file format modifies column names.
Creates a DataFrame with various column name patterns, saves as parquet, 
then reloads to compare column names.
"""
import pandas as pd
import numpy as np
from pathlib import Path

def test_parquet_column_names():
    """Test if parquet modifies column names"""
    
    print("TESTING PARQUET COLUMN NAME HANDLING")
    print("="*50)
    
    # Create test DataFrame with various column name patterns
    np.random.seed(42)
    n_rows = 1000
    
    data = {
        # Regular column names
        'normal_column': np.random.randint(1, 10, n_rows),
        'UPPERCASE_COL': np.random.choice(['A', 'B', 'C'], n_rows),
        'MixedCase': np.random.random(n_rows),
        
        # Underscore prefixed columns (like BRFSS calculated variables)
        '_DRDXAR2': np.random.choice([1, 2], n_rows),
        '_STATE': np.random.randint(1, 50, n_rows),
        '_AGE65YR': np.random.choice([1, 2], n_rows),
        '_BMI5CAT': np.random.randint(1, 4, n_rows),
        
        # Description columns
        'normal_column_DESC': np.random.choice(['Desc A', 'Desc B'], n_rows),
        'X_STATE_DESC': np.random.choice(['State A', 'State B'], n_rows),
        'X_DRDXAR2_DESC': np.random.choice(['Yes', 'No'], n_rows),
        
        # Edge cases
        'x_lowercase': np.random.randint(1, 5, n_rows),
        'X_UPPERCASE': np.random.randint(1, 5, n_rows),
        '__double_underscore': np.random.random(n_rows),
        'column_with_numbers_123': np.random.randint(1, 100, n_rows),
        'column.with.dots': np.random.random(n_rows),
        'column with spaces': np.random.choice(['A', 'B'], n_rows),
    }
    
    df_original = pd.DataFrame(data)
    
    print(f"Original DataFrame shape: {df_original.shape}")
    print(f"Original column names ({len(df_original.columns)}):")
    for i, col in enumerate(df_original.columns):
        print(f"  {i+1:2d}. '{col}'")
    
    # Test different parquet engines and settings
    test_file = Path("/Users/sksizer/dev/dat490/data/test_column_names.parquet")
    
    engines = ['pyarrow', 'fastparquet']
    index_settings = [True, False]
    
    for engine in engines:
        if engine == 'fastparquet':
            try:
                import fastparquet
            except ImportError:
                print(f"\n⚠️  Skipping {engine} (not installed)")
                continue
        
        for use_index in index_settings:
            print(f"\n{'='*50}")
            print(f"TESTING: engine='{engine}', index={use_index}")
            print(f"{'='*50}")
            
            try:
                # Save DataFrame
                print(f"Saving with engine='{engine}', index={use_index}...")
                df_original.to_parquet(test_file, engine=engine, index=use_index)
                
                # Reload DataFrame
                print(f"Loading with engine='{engine}'...")
                df_reloaded = pd.read_parquet(test_file, engine=engine)
                
                print(f"Reloaded DataFrame shape: {df_reloaded.shape}")
                print(f"Reloaded column names ({len(df_reloaded.columns)}):")
                for i, col in enumerate(df_reloaded.columns):
                    print(f"  {i+1:2d}. '{col}'")
                
                # Compare column names
                original_cols = set(df_original.columns)
                reloaded_cols = set(df_reloaded.columns)
                
                if original_cols == reloaded_cols:
                    print("✅ Column names UNCHANGED")
                else:
                    print("❌ Column names CHANGED")
                    
                    added = reloaded_cols - original_cols
                    removed = original_cols - reloaded_cols
                    
                    if added:
                        print(f"  Added columns: {sorted(added)}")
                    if removed:
                        print(f"  Removed columns: {sorted(removed)}")
                    
                    # Check for renaming patterns
                    print("\n  Potential renaming patterns:")
                    for orig_col in removed:
                        for new_col in added:
                            if orig_col.lstrip('_') in new_col or new_col.lstrip('X_') == orig_col.lstrip('_'):
                                print(f"    '{orig_col}' → '{new_col}'")
                
                # Check data integrity for key columns
                test_cols = ['_DRDXAR2', 'normal_column'] if '_DRDXAR2' in df_reloaded.columns else ['normal_column']
                for col in test_cols:
                    if col in df_original.columns and col in df_reloaded.columns:
                        if df_original[col].equals(df_reloaded[col]):
                            print(f"✅ Data integrity for '{col}': OK")
                        else:
                            print(f"❌ Data integrity for '{col}': CHANGED")
                
            except Exception as e:
                print(f"❌ Error with engine='{engine}', index={use_index}: {e}")
    
    # Clean up test file
    if test_file.exists():
        test_file.unlink()
        print(f"\n🧹 Cleaned up test file: {test_file}")
    
    print(f"\n🎉 Test complete!")

if __name__ == "__main__":
    test_parquet_column_names()