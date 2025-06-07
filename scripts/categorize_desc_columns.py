#!/usr/bin/env python3
"""
Convert all _DESC columns in LLCP2023_desc.parquet to categorical dtype.
This reduces memory usage significantly and improves performance for categorical data.
"""
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def categorize_desc_columns():
    """
    Load LLCP2023_desc.parquet, convert _DESC columns to categorical using the exact original approach,
    and save as LLCP2023_desc_categorized.parquet
    """
    data_dir = Path("/Users/sksizer/dev/dat490/data")
    input_file = data_dir / "LLCP2023_desc.parquet"
    output_file = data_dir / "LLCP2023_desc_categorized.parquet"
    
    # Check if input file exists
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return
    
    logger.info(f"Loading data from {input_file}...")
    
    # Step 1: Load the Parquet file (using pyarrow like original)
    df = pd.read_parquet(input_file, engine='pyarrow')
    logger.info(f"Loaded DataFrame with shape: {df.shape}")
    
    # Step 2: Find columns ending with '_DESC' and convert to 'category'
    desc_cols = [col for col in df.columns if col.endswith('_DESC')]
    logger.info(f"Found {len(desc_cols)} _DESC columns to categorize")
    
    if not desc_cols:
        logger.warning("No _DESC columns found in the dataset")
        return
    
    # Show memory usage before conversion
    memory_before = df.memory_usage(deep=True).sum() / 1024**2  # MB
    logger.info(f"Memory usage before categorization: {memory_before:.1f} MB")
    
    # Check for problematic columns before conversion
    problematic_cols = []
    for col in desc_cols:
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) == 0:
            logger.warning(f"Column {col} has no non-null values")
            problematic_cols.append(col)
        elif len(unique_vals) > 10000:  # Too many categories might be problematic
            logger.warning(f"Column {col} has {len(unique_vals)} unique values (might be inefficient as categorical)")
    
    logger.info("Converting _DESC columns to categorical dtype...")
    
    # Convert using the exact same approach as original code
    try:
        df[desc_cols] = df[desc_cols].astype('category')
        logger.info("✅ Successfully converted all _DESC columns to categorical")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        # Try converting individually to identify problematic columns
        logger.info("Trying individual column conversion...")
        failed_cols = []
        for col in desc_cols:
            try:
                df[col] = df[col].astype('category')
                logger.debug(f"  ✅ {col}")
            except Exception as col_e:
                logger.warning(f"  ❌ {col}: {col_e}")
                failed_cols.append(col)
        
        if failed_cols:
            logger.warning(f"Failed to convert {len(failed_cols)} columns: {failed_cols}")
    
    # Show memory usage after conversion
    memory_after = df.memory_usage(deep=True).sum() / 1024**2  # MB
    memory_saved = memory_before - memory_after
    memory_saved_pct = (memory_saved / memory_before) * 100 if memory_before > 0 else 0
    
    logger.info(f"Memory usage after categorization: {memory_after:.1f} MB")
    logger.info(f"Memory saved: {memory_saved:.1f} MB ({memory_saved_pct:.1f}%)")
    
    # Step 3: Save modified DataFrame to a new Parquet file (using exact same approach)
    logger.info(f"Saving categorized data to {output_file}...")
    df.to_parquet(output_file, engine='pyarrow', index=True)
    
    # Verification
    logger.info("Verifying saved file...")
    df_verify = pd.read_parquet(output_file, engine='pyarrow')
    
    # Check that _DESC columns are categorical
    categorical_desc_cols = [col for col in df_verify.columns 
                           if col.endswith('_DESC') and df_verify[col].dtype.name == 'category']
    
    non_categorical_desc_cols = [col for col in df_verify.columns 
                               if col.endswith('_DESC') and df_verify[col].dtype.name != 'category']
    
    logger.info(f"Verification: {len(categorical_desc_cols)} _DESC columns are categorical")
    
    if non_categorical_desc_cols:
        logger.warning(f"Non-categorical _DESC columns: {non_categorical_desc_cols}")
        for col in non_categorical_desc_cols:
            unique_count = df_verify[col].dropna().nunique()
            total_count = len(df_verify[col])
            null_count = df_verify[col].isnull().sum()
            logger.info(f"  {col}: {unique_count} unique, {null_count} nulls, {total_count} total")
    
    if len(categorical_desc_cols) == len(desc_cols):
        logger.info("✅ SUCCESS: All _DESC columns successfully converted to categorical")
    else:
        logger.warning(f"⚠️  WARNING: Only {len(categorical_desc_cols)} out of {len(desc_cols)} _DESC columns are categorical")
    
    # Check column names haven't changed
    if set(df.columns) == set(df_verify.columns):
        logger.info("✅ Column names unchanged")
    else:
        logger.warning("❌ Column names changed during save/load!")
        
    # Check data shape
    if df.shape == df_verify.shape:
        logger.info(f"✅ Data shape unchanged: {df.shape}")
    else:
        logger.warning(f"❌ Data shape changed: {df.shape} -> {df_verify.shape}")
    
    # Show file sizes
    input_size = input_file.stat().st_size / 1024**2  # MB
    output_size = output_file.stat().st_size / 1024**2  # MB
    size_change = output_size - input_size
    size_change_pct = (size_change / input_size) * 100 if input_size > 0 else 0
    
    logger.info(f"\nFile size comparison:")
    logger.info(f"  Original: {input_size:.1f} MB")
    logger.info(f"  Categorized: {output_size:.1f} MB")
    if size_change >= 0:
        logger.info(f"  Change: +{size_change:.1f} MB (+{size_change_pct:.1f}%)")
    else:
        logger.info(f"  Saved: {abs(size_change):.1f} MB ({abs(size_change_pct):.1f}%)")
    
    logger.info(f"\n🎉 Categorization complete! Output saved to: {output_file}")

def main():
    """Main function to run the categorization process"""
    try:
        categorize_desc_columns()
    except Exception as e:
        logger.error(f"Error during categorization: {e}")
        raise

if __name__ == "__main__":
    main()