from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.chat_models.fake import FakeListChatModel
from sqlalchemy import create_engine
import duckdb
import os

# Always write to the same DuckDB file
DB_PATH = "my_temp.db"

# Delete old DB if you want a fresh load (optional)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Step 1: Load CSVs into the DuckDB file
con = duckdb.connect(DB_PATH)
con.execute("CREATE TABLE customers AS SELECT * FROM read_csv_auto('../../data/structured/customers.csv');")
con.execute("CREATE TABLE orders AS SELECT * FROM read_csv_auto('../../data/structured/orders.csv');")
con.execute("CREATE TABLE emissions AS SELECT * FROM read_csv_auto('../../data/structured/emissions.csv');")
con.close()

# Step 2: Create SQLAlchemy engine pointing to the same file
engine = create_engine(f"duckdb:///{DB_PATH}")
db = SQLDatabase(engine=engine)

# Step 3: Fake LLM to return correct SQL
llm = FakeListChatModel(responses=[
    "SELECT c.name FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.amount > 500;"
])



db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)

def query_sql(question):
    return db_chain.invoke({"query": question})["result"]

if __name__ == "__main__":
    print(query_sql("Which customers placed an order over $500?"))

