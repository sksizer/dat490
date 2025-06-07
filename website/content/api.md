# API Documentation

## BFRSS Module

The `dat490.bfrss` module provides a convenient Python interface for working with BRFSS (Behavioral Risk Factor Surveillance System) data and metadata.

### Core Classes

#### BFRSS

The main wrapper class for BRFSS data and metadata.

```python
from dat490 import BFRSS, load_bfrss, load_bfrss_components, setup_bfrss_logger

# Initialize BFRSS wrapper
bfrss = BFRSS(
    data_path=None,           # Optional: Path to parquet file
    codebook_path=None,       # Optional: Path to codebook HTML
    exclude_desc_columns=True, # Exclude _DESC columns from metadata
    semantically_null=False,  # Convert missing indicators to NaN
    root_dir=None            # Optional: Root directory for file search
)

# Access data and metadata (lazy loading)
df = bfrss.df
metadata = bfrss.metadata
```

### Convenience Functions

#### load_bfrss()

Quick way to create a BFRSS instance with default settings.

```python
# Basic usage
bfrss = load_bfrss()

# With semantic null conversion
bfrss = load_bfrss(semantically_null=True)

# Custom options
bfrss = load_bfrss(
    exclude_desc_columns=False,
    semantically_null=True,
    root_dir="/path/to/data"
)
```

#### load_bfrss_components()

Load data, metadata, and logger for destructured assignment.

```python
# Basic destructured assignment
df, metadata, logger = load_bfrss_components()

# With semantic null conversion
df, metadata, logger = load_bfrss_components(semantically_null=True)

# Custom options
df, metadata, logger = load_bfrss_components(
    exclude_desc_columns=False,
    semantically_null=True,
    root_dir="/path/to/data"
)
```

#### setup_bfrss_logger()

Create a clean logger for BFRSS operations.

```python
import logging

# Default INFO level
logger = setup_bfrss_logger()

# Custom log level
logger = setup_bfrss_logger(level=logging.DEBUG)
```

### Semantic Null Handling

**Semantic nulls** are numeric values that indicate missing, refused, or unknown responses according to the BRFSS codebook metadata.

#### What are Semantic Nulls?

In BRFSS data, certain numeric codes represent missing information:
- `7` = "Don't know/Not Sure"
- `9` = "Refused"
- `77` = "Don't know/Not Sure" (for 2-digit variables)
- `99` = "Refused" (for 2-digit variables)

These values are present in the data as numbers but should be treated as missing for analysis.

#### Using Semantic Null Conversion

```python
# Convert semantic nulls during data loading
bfrss = BFRSS(semantically_null=True)
df = bfrss.df  # Missing indicators are now NaN

# Or use convenience functions
df, metadata, logger = load_bfrss_components(semantically_null=True)

# Convert semantic nulls on existing DataFrame
bfrss = BFRSS()  # Don't convert during loading
df = bfrss.df
df_clean = bfrss.convert_semantic_nulls(df)  # Convert all columns
df_partial = bfrss.convert_semantic_nulls(df, columns=['GENHLTH', 'SEX'])  # Specific columns
```

#### Finding Semantic Null Values

```python
# Get missing indicator values for a specific column
missing_vals = bfrss.get_semantic_null_values('GENHLTH')
# Returns: {7, 9} for GENHLTH

# Get mapping for all columns
null_mapping = bfrss.get_semantic_null_mapping()
# Returns: {'GENHLTH': {7, 9}, 'SEX': {9}, ...}
```

### Data Access Methods

#### Basic Data Access

```python
# Get DataFrame and metadata
df = bfrss.df
metadata = bfrss.metadata

# Create copies
df_copy = bfrss.cloneDF()
metadata_copy = bfrss.cloneMetadata()
```

#### Value Lookup and Translation

```python
# Look up description for a specific value
desc = bfrss.lookup_value('GENHLTH', 1)
# Returns: "Excellent"

# Translate entire column to descriptions
translated = bfrss.translate_column('GENHLTH')
# Returns Series with descriptive labels instead of codes
```

#### Column Filtering and Search

```python
# Get columns by section
demo_columns = bfrss.get_columns_by_section('Demographics')

# Get all sections
sections = bfrss.get_sections()

# Search columns by keywords
health_columns = bfrss.search_columns('health')

# Get column metadata
column_info = bfrss.get_column_info('GENHLTH')
```

### Metadata Structure

Each column's metadata includes:

- **label**: Human-readable column description
- **sas_variable_name**: Original SAS variable name
- **section_name**: Survey section (e.g., "Demographics", "Health Status")
- **question**: Survey question text
- **value_ranges**: List of valid values and their descriptions
- **statistics**: Statistical summary (counts, means, etc.)
- **indicates_missing**: Flag for values representing missing data

### Example Usage

```python
from dat490 import load_bfrss_components
import pandas as pd

# Load data with semantic null conversion
df, metadata, logger = load_bfrss_components(semantically_null=True)

# Get demographic columns for analysis
bfrss = load_bfrss()
demo_cols = bfrss.get_columns_by_section('Demographics')

# Filter to meaningful data (excluding missing indicators)
model_df = df[demo_cols + ['GENHLTH']].dropna()

# Log summary
logger.info(f"Analysis dataset: {len(model_df)} rows, {len(model_df.columns)} columns")
```

### Error Handling

The module handles common issues gracefully:

- **File not found**: Searches common locations for data files
- **Missing metadata**: Skips columns without valid value definitions
- **Type conversion**: Handles mixed data types in semantic null conversion
- **Memory efficiency**: Uses lazy loading for large datasets

### Performance Notes

- **Lazy loading**: Data and metadata are loaded only when first accessed
- **Caching**: Semantic null mappings are cached to avoid recomputation
- **Memory efficiency**: Use `cloneDF()` and `cloneMetadata()` to avoid copying large objects unnecessarily
- **Logging**: Use provided logger to track data loading and processing steps