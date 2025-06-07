#!/usr/bin/env python3
"""
Compare columns between BRFSS parquet files and check for specific columns like _DRDXAR2.
"""
import pandas as pd
from pathlib import Path

def check_parquet_columns():
    """Compare columns between the three BRFSS parquet files"""
    data_dir = Path("/Users/sksizer/dev/dat490/data")
    files = {
        "LLCP2023": data_dir / "LLCP2023.parquet",
        "LLCP2023_desc": data_dir / "LLCP2023_desc.parquet", 
        "LLCP2023_desc_categorized": data_dir / "LLCP2023_desc_categorized.parquet"
    }
    
    print("BRFSS PARQUET FILES COLUMN COMPARISON")
    print("="*50)
    
    # Check file existence and get columns
    columns_dict = {}
    for name, path in files.items():
        if not path.exists():
            print(f"❌ {name} not found")
            continue
            
        try:
            import pyarrow.parquet as pq
            parquet_file = pq.ParquetFile(path)
            columns = parquet_file.schema.names
            columns_dict[name] = set(columns)
            print(f"✅ {name}: {len(columns)} columns")
        except Exception as e:
            print(f"❌ Error reading {name}: {e}")
    
    if len(columns_dict) < 2:
        print("Need at least 2 files to compare")
        return
    
    # Check for _DRDXAR2 specifically
    print(f"\n🔍 CHECKING FOR _DRDXAR2:")
    for name, cols in columns_dict.items():
        if "_DRDXAR2" in cols:
            print(f"  ✅ {name}: Contains _DRDXAR2")
        elif any("DRDXAR2" in col for col in cols):
            drdx_cols = [col for col in cols if "DRDXAR2" in col]
            print(f"  ⚠️  {name}: Missing _DRDXAR2, but has: {drdx_cols}")
        else:
            print(f"  ❌ {name}: No DRDXAR2 columns found")
    
    # Show _DESC column counts
    print(f"\n📊 _DESC COLUMNS:")
    for name, cols in columns_dict.items():
        desc_cols = [col for col in cols if col.endswith('_DESC')]
        print(f"  {name}: {len(desc_cols)} _DESC columns")
    
    # Show overlap
    if len(columns_dict) >= 2:
        names = list(columns_dict.keys())
        if len(names) == 3:
            common = columns_dict[names[0]] & columns_dict[names[1]] & columns_dict[names[2]]
            print(f"\n🤝 COMMON TO ALL: {len(common)} columns")
        
        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                overlap = len(columns_dict[name1] & columns_dict[name2])
                total = len(columns_dict[name1] | columns_dict[name2])
                pct = overlap / total * 100 if total > 0 else 0
                print(f"  {name1} ∩ {name2}: {overlap}/{total} ({pct:.1f}%)")

def check_categorization():
    """Check if _DESC columns are properly categorized"""
    data_dir = Path("/Users/sksizer/dev/dat490/data")
    cat_file = data_dir / "LLCP2023_desc_categorized.parquet"
    
    if not cat_file.exists():
        print("❌ Categorized file not found")
        return
    
    print(f"\n🏷️  CATEGORIZATION CHECK:")
    df = pd.read_parquet(cat_file)
    
    desc_cols = [col for col in df.columns if col.endswith('_DESC')]
    categorical_cols = [col for col in desc_cols if df[col].dtype.name == 'category']
    non_categorical_cols = [col for col in desc_cols if df[col].dtype.name != 'category']
    
    print(f"  Total _DESC columns: {len(desc_cols)}")
    print(f"  Categorical: {len(categorical_cols)}")
    print(f"  Non-categorical: {len(non_categorical_cols)}")
    
    if non_categorical_cols:
        print(f"  Non-categorical columns: {non_categorical_cols}")
        for col in non_categorical_cols:
            null_count = df[col].isnull().sum()
            total = len(df[col])
            print(f"    {col}: {null_count}/{total} nulls")

if __name__ == "__main__":
    check_parquet_columns()
    check_categorization()