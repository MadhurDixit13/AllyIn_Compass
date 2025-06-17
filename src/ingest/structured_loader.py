import duckdb
import pandas as pd
import os

# # Always write to the same DuckDB file
# DB_PATH = "../../data/structured/my_temp.db"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "structured", "my_temp.db")
# Delete old DB if you want a fresh load (optional)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


def load_csv_to_duckdb(folder_path):
    con = duckdb.connect(database=DB_PATH)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            table_name = filename.replace('.csv', '')
            df = pd.read_csv(os.path.join(folder_path, filename))
            con.register(table_name, df)
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}")
            print(f"Loaded {table_name} into DuckDB")

    return con

if __name__ == "__main__":
    con = load_csv_to_duckdb('../../data/structured')
    print(con.sql("SELECT * FROM customers LIMIT 10").df())
    print(con.sql("SELECT * FROM orders LIMIT 10").df())
    print(con.sql("SELECT * FROM emissions LIMIT 10").df())
    # Close the connection
    # con.close()
# This script loads all CSV files from a specified folder into DuckDB in memory.