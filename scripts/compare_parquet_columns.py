#!/usr/bin/env python3
"""
Compare columns between different BRFSS parquet files
"""
import pandas as pd
from pathlib import Path

def compare_parquet_columns():
    # Define file paths
    data_dir = Path("/Users/sksizer/dev/dat490/data")
    files = {
        "LLCP2023": data_dir / "LLCP2023.parquet",
        "LLCP2023_desc": data_dir / "LLCP2023_desc.parquet",
        "LLCP2023_desc_categorized": data_dir / "LLCP2023_desc_categorized.parquet"
    }
    
    # Check if all files exist
    for name, path in files.items():
        if not path.exists():
            print(f"❌ {name} not found at {path}")
            return
    
    # Read columns from each file
    columns_dict = {}
    for name, path in files.items():
        print(f"\n📁 Reading {name}...")
        try:
            # Try to read parquet schema without loading data
            import pyarrow.parquet as pq
            parquet_file = pq.ParquetFile(path)
            columns = parquet_file.schema.names
            columns_dict[name] = set(columns)
            print(f"   Found {len(columns)} columns")
        except Exception as e:
            try:
                # Fallback: read with pandas
                df = pd.read_parquet(path)
                columns_dict[name] = set(df.columns)
                print(f"   Found {len(df.columns)} columns (using pandas fallback)")
            except Exception as e2:
                print(f"   ❌ Error reading {name}: {e}")
                print(f"   ❌ Pandas fallback also failed: {e2}")
                return
    
    # Print column comparison
    print("\n" + "="*60)
    print("COLUMN COMPARISON")
    print("="*60)
    
    # Find common columns
    common_cols = columns_dict["LLCP2023"] & columns_dict["LLCP2023_desc"] & columns_dict["LLCP2023_desc_categorized"]
    print(f"\n✅ Common columns in all three files: {len(common_cols)}")
    
    # Find unique columns in each file
    for name, cols in columns_dict.items():
        other_cols = [c for n, c in columns_dict.items() if n != name]
        if other_cols:
            unique = cols.difference(*other_cols)
        else:
            unique = cols
        if unique:
            print(f"\n🔸 Unique to {name}: {len(unique)} columns")
            for col in sorted(list(unique))[:10]:  # Show first 10
                print(f"   - {col}")
            if len(unique) > 10:
                print(f"   ... and {len(unique) - 10} more")
    
    # Check specifically for _DRDXAR2
    print("\n" + "="*60)
    print("CHECKING FOR _DRDXAR2")
    print("="*60)
    
    target_col = "_DRDXAR2"
    for name, cols in columns_dict.items():
        if target_col in cols:
            print(f"✅ {name}: Contains {target_col}")
        else:
            print(f"❌ {name}: Missing {target_col}")
            # Look for similar column names
            similar = [col for col in cols if "DRDX" in col or "AR2" in col]
            if similar:
                print(f"   Similar columns found: {similar}")
    
    # Print column differences between files
    print("\n" + "="*60)
    print("DETAILED DIFFERENCES")
    print("="*60)
    
    # Compare LLCP2023 vs LLCP2023_desc
    diff_1_2 = columns_dict["LLCP2023"] - columns_dict["LLCP2023_desc"]
    if diff_1_2:
        print(f"\n📍 In LLCP2023 but not in LLCP2023_desc: {len(diff_1_2)}")
        for col in sorted(list(diff_1_2))[:5]:
            print(f"   - {col}")
        if len(diff_1_2) > 5:
            print(f"   ... and {len(diff_1_2) - 5} more")
    
    diff_2_1 = columns_dict["LLCP2023_desc"] - columns_dict["LLCP2023"]
    if diff_2_1:
        print(f"\n📍 In LLCP2023_desc but not in LLCP2023: {len(diff_2_1)}")
        for col in sorted(list(diff_2_1))[:5]:
            print(f"   - {col}")
        if len(diff_2_1) > 5:
            print(f"   ... and {len(diff_2_1) - 5} more")
    
    # Compare LLCP2023_desc vs LLCP2023_desc_categorized
    diff_2_3 = columns_dict["LLCP2023_desc"] - columns_dict["LLCP2023_desc_categorized"]
    if diff_2_3:
        print(f"\n📍 In LLCP2023_desc but not in LLCP2023_desc_categorized: {len(diff_2_3)}")
        for col in sorted(list(diff_2_3))[:5]:
            print(f"   - {col}")
        if len(diff_2_3) > 5:
            print(f"   ... and {len(diff_2_3) - 5} more")
    
    diff_3_2 = columns_dict["LLCP2023_desc_categorized"] - columns_dict["LLCP2023_desc"]
    if diff_3_2:
        print(f"\n📍 In LLCP2023_desc_categorized but not in LLCP2023_desc: {len(diff_3_2)}")
        for col in sorted(list(diff_3_2))[:5]:
            print(f"   - {col}")
        if len(diff_3_2) > 5:
            print(f"   ... and {len(diff_3_2) - 5} more")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    for name, cols in columns_dict.items():
        print(f"{name}: {len(cols)} columns")
    
    # Save full column lists to files for detailed inspection
    output_dir = Path("/Users/sksizer/dev/dat490/data")
    for name, cols in columns_dict.items():
        output_file = output_dir / f"{name}_columns.txt"
        with open(output_file, 'w') as f:
            f.write(f"Columns in {name} ({len(cols)} total):\n")
            f.write("="*60 + "\n")
            for col in sorted(cols):
                f.write(f"{col}\n")
        print(f"\n💾 Full column list saved to: {output_file}")

if __name__ == "__main__":
    compare_parquet_columns()