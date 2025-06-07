# Scripts Directory

This directory contains utility scripts for working with BRFSS data.

## Scripts

### Data Processing

- **`categorize_desc_columns.py`** - Convert `_DESC` columns to categorical dtype for memory efficiency
  - Input: `data/LLCP2023_desc.parquet`
  - Output: `data/LLCP2023_desc_categorized.parquet`
  - Reduces memory usage by ~87% (10.7GB → 1.4GB)
  - Usage: `python scripts/categorize_desc_columns.py`

- **`generate.py`** - Generate metadata from BRFSS codebook HTML
  - Processes `data/codebook_USCODE23_LLCP_021924.HTML`
  - Creates structured metadata for the web application

### Analysis & Verification

- **`check_parquet_columns.py`** - Quick column comparison and verification
  - Compares columns across all three parquet files
  - Checks for `_DRDXAR2` column availability
  - Verifies categorization status
  - Usage: `python scripts/check_parquet_columns.py`

- **`compare_parquet_columns.py`** - Detailed column comparison analysis
  - Comprehensive comparison between parquet files
  - Saves detailed column lists to text files
  - Usage: `python scripts/compare_parquet_columns.py`

## Key Findings

- **`_DRDXAR2` Column**: Present as `_DRDXAR2` in original file, renamed to `X_DRDXAR2` in desc versions
- **Memory Optimization**: Categorizing `_DESC` columns saves 87% memory usage
- **File Compatibility**: All files maintain same row count (433,323 rows)
- **Known Issue**: `IYEAR_DESC` column contains all null values and cannot be categorized

## Usage Tips

1. Use `check_parquet_columns.py` for quick verification
2. Run `categorize_desc_columns.py` to optimize memory usage
3. When working with BFRSS wrapper, use `X_DRDXAR2` instead of `_DRDXAR2` for desc files