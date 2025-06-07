"""
BFRSS Data Wrapper
Provides a convenient interface for working with BRFSS data and metadata.
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from .parser import parse_codebook_html, ColumnMetadata, ValueRange

# Configure logger for this module
logger = logging.getLogger(__name__)


def setup_bfrss_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Set up a clean logger for BFRSS data operations.
    
    Args:
        level: Logging level (default: logging.INFO)
        
    Returns:
        Configured logger instance
    """
    # Create or get logger
    bfrss_logger = logging.getLogger('bfrss_analysis')
    
    # Clear any existing handlers to avoid duplicates
    bfrss_logger.handlers.clear()
    
    # Set level
    bfrss_logger.setLevel(level)
    
    # Create formatter for clean output
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create handler for console output
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    bfrss_logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate messages
    bfrss_logger.propagate = False
    
    return bfrss_logger


class BFRSS:
    """
    Wrapper class for BRFSS data and metadata.
    
    Provides methods for:
    - Loading and accessing BRFSS data
    - Parsing and accessing codebook metadata
    - Looking up value descriptions
    - Filtering columns by sections
    """
    
    def __init__(self, 
                 data_path: Optional[Union[str, Path]] = None,
                 codebook_path: Optional[Union[str, Path]] = None,
                 exclude_desc_columns: bool = True,
                 root_dir: Optional[Union[str, Path]] = None):
        """
        Initialize BFRSS wrapper.
        
        Args:
            data_path: Path to LLCP2023_desc_categorized.parquet file
            codebook_path: Path to codebook HTML file
            exclude_desc_columns: Whether to exclude _DESC columns from metadata generation
            root_dir: Root directory to search for data files (optional)
        """
        # Set root directory for file searching
        self.root_dir = Path(root_dir) if root_dir else None
        
        # Set default paths if not provided
        self.data_path = Path(data_path) if data_path else self._find_data_file('LLCP2023_desc_categorized.parquet')
        self.codebook_path = Path(codebook_path) if codebook_path else self._find_data_file('codebook_USCODE23_LLCP_021924.HTML')
        self.exclude_desc_columns = exclude_desc_columns
        
        # Lazy loading - data loaded on first access
        self._df = None
        self._metadata = None
        
    def _find_data_file(self, filename: str) -> Path:
        """Find data file in common locations."""
        # Check common paths
        possible_paths = [
            Path('data') / filename,
            Path('..') / 'data' / filename,
            Path('dat490') / 'data' / filename,
            Path.cwd() / 'data' / filename,
        ]
        
        # If root_dir is specified, check there first
        if self.root_dir:
            root_paths = [
                self.root_dir / 'data' / filename,
                self.root_dir / filename,
            ]
            possible_paths = root_paths + possible_paths
        
        for path in possible_paths:
            if path.exists():
                return path
                
        raise FileNotFoundError(f"Could not find {filename} in common locations. Please specify path explicitly.")
    
    @property
    def df(self) -> pd.DataFrame:
        """Load and return the main DataFrame (lazy loading)."""
        if self._df is None:
            logger.info(f"Loading data from {self.data_path}...")
            self._df = pd.read_parquet(self.data_path)
            logger.info(f"Loaded {len(self._df)} rows and {len(self._df.columns)} columns")
        return self._df
    
    
    @property
    def metadata(self) -> Dict[str, ColumnMetadata]:
        """Parse and return metadata (lazy loading)."""
        if self._metadata is None:
            logger.info(f"Parsing codebook from {self.codebook_path}...")
            
            # Determine which DataFrame to use for statistics
            df_for_stats = self.df
            if self.exclude_desc_columns:
                # Filter out _DESC columns for statistics calculation
                non_desc_columns = [col for col in df_for_stats.columns if not col.endswith('_DESC')]
                df_for_stats = df_for_stats[non_desc_columns]
                logger.info(f"Excluding {len(self.df.columns) - len(non_desc_columns)} _DESC columns from metadata generation")
            
            self._metadata = parse_codebook_html(self.codebook_path, df_for_stats)
            logger.info(f"Parsed metadata for {len(self._metadata)} columns")
        return self._metadata
    
    def cloneDF(self) -> pd.DataFrame:
        """Return a copy of the DataFrame."""
        return self.df.copy()
    
    def cloneMetadata(self) -> Dict[str, ColumnMetadata]:
        """Return a copy of the metadata dictionary."""
        return self.metadata.copy()
    
    def lookup_value(self, column_name: str, value: Union[int, float, None]) -> str:
        """
        Look up the description for a specific value in a column.
        
        Args:
            column_name: The column name (SAS variable name)
            value: The value to look up
            
        Returns:
            Description string or "Unknown" if not found
        """
        if column_name not in self.metadata:
            return f"Column {column_name} not found"
        
        if pd.isna(value):
            return "Missing"
        
        column_meta = self.metadata[column_name]
        
        # Try to convert to int if possible
        try:
            value_int = int(value)
        except (TypeError, ValueError):
            return f"Unknown value: {value}"
        
        # Search through value ranges
        for val_def in column_meta.value_ranges:
            if isinstance(val_def, ValueRange) and val_def.start <= value_int <= val_def.end:
                return val_def.description
        
        return f"Unknown code: {value}"
    
    def translate_column(self, column_name: str, series: Optional[pd.Series] = None) -> pd.Series:
        """
        Translate all values in a column to their descriptions.
        
        Args:
            column_name: The column name to translate
            series: Optional series to translate. If None, uses the column from the main DataFrame
            
        Returns:
            Series with translated values
        """
        if series is None:
            if column_name not in self.df.columns:
                raise ValueError(f"Column {column_name} not found in DataFrame")
            series = self.df[column_name]
        
        return series.apply(lambda x: self.lookup_value(column_name, x))
    
    def get_columns_by_section(self, section_name: Optional[str] = None) -> List[str]:
        """
        Get column names filtered by section.
        
        Args:
            section_name: Name of the section to filter by. If None, returns all columns grouped by section.
            
        Returns:
            List of column names in the specified section, or dict of section -> columns if section_name is None
        """
        if section_name is None:
            # Return all columns grouped by section
            sections = {}
            for col_name, col_meta in self.metadata.items():
                section = col_meta.section_name or "No Section"
                if section not in sections:
                    sections[section] = []
                sections[section].append(col_name)
            return sections
        else:
            # Return columns for specific section
            return [
                col_name 
                for col_name, col_meta in self.metadata.items() 
                if col_meta.section_name == section_name
            ]
    
    def get_sections(self) -> List[str]:
        """Get list of all unique section names."""
        sections = set()
        for col_meta in self.metadata.values():
            if col_meta.section_name:
                sections.add(col_meta.section_name)
        return sorted(list(sections))
    
    def get_column_info(self, column_name: str) -> Optional[ColumnMetadata]:
        """Get metadata for a specific column."""
        return self.metadata.get(column_name)
    
    def search_columns(self, search_term: str, in_label: bool = True, in_question: bool = True) -> List[str]:
        """
        Search for columns containing a search term.
        
        Args:
            search_term: Term to search for (case-insensitive)
            in_label: Search in column labels
            in_question: Search in question text
            
        Returns:
            List of matching column names
        """
        search_term = search_term.lower()
        matches = []
        
        for col_name, col_meta in self.metadata.items():
            if in_label and col_meta.label and search_term in col_meta.label.lower():
                matches.append(col_name)
            elif in_question and col_meta.question and search_term in col_meta.question.lower():
                matches.append(col_name)
                
        return matches
    
    def get_components(self) -> Tuple[pd.DataFrame, Dict[str, ColumnMetadata], logging.Logger]:
        """
        Get DataFrame, metadata, and logger for destructured assignment.
        
        Returns:
            Tuple of (DataFrame, metadata dict, logger)
        """
        logger = setup_bfrss_logger()
        return self.cloneDF(), self.cloneMetadata(), logger


def load_bfrss(exclude_desc_columns: bool = True, root_dir: Optional[Union[str, Path]] = None) -> BFRSS:
    """
    Convenience function to load BFRSS data with default settings.
    
    Args:
        exclude_desc_columns: Whether to exclude _DESC columns from metadata generation
        root_dir: Root directory to search for data files (optional)
        
    Returns:
        BFRSS wrapper object
    """
    return BFRSS(exclude_desc_columns=exclude_desc_columns, root_dir=root_dir)


def load_bfrss_components(exclude_desc_columns: bool = True, root_dir: Optional[Union[str, Path]] = None) -> Tuple[pd.DataFrame, Dict[str, ColumnMetadata], logging.Logger]:
    """
    Convenience function to load BFRSS data and return components for destructured assignment.
    
    Args:
        exclude_desc_columns: Whether to exclude _DESC columns from metadata generation
        root_dir: Root directory to search for data files (optional)
        
    Returns:
        Tuple of (DataFrame, metadata dict, logger)
        
    Example:
        df, metadata, logger = load_bfrss_components()
    """
    bfrss = load_bfrss(exclude_desc_columns=exclude_desc_columns, root_dir=root_dir)
    return bfrss.get_components()