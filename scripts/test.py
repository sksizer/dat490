import pyarrow.parquet as pq

table = pq.read_table('../data/LLCP2023_desc_categorized.parquet')
print(table.column_names)