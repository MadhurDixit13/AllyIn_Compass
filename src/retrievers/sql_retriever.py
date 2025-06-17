from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_groq import ChatGroq
from sqlalchemy import create_engine
import os
import dotenv
import re

# Load environment variables (make sure GROQ_API_KEY is set in your .env)
dotenv.load_dotenv()

# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
# DB_PATH = os.path.join(PROJECT_ROOT, "data", "structured", "my_temp.db")

# # Always write to the same DuckDB file
DB_PATH = "../../data/structured/my_temp.db"

# Step 1: Create SQLAlchemy engine
engine = create_engine(f"duckdb:///{DB_PATH}")
db = SQLDatabase(engine=engine)

# Step 2: Initialize Groq LLM using LangChain wrapper
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),  # Ensure you have set this in your .env file
    model_name="llama3-70b-8192",  # or use llama3-8b-8192, gemma-7b-it
    temperature=0
)

# Step 3: Create SQLDatabaseChain
db_chain = SQLDatabaseChain.from_llm(llm=llm, 
                                     db=db, 
                                     verbose=True,
                                    #  use_query_checker=True,  # enables basic syntax checking
                                    #  return_intermediate_steps=True
                                     )


def query_sql(question: str) -> str:
    result = db_chain.invoke({"query": question})
    rows = result.get("result", [])  # ensure safe access
    if not rows:
        return "No matching records found."

    # Format for human readability
    flat_result = ", ".join(str(row[0]) for row in rows)
    return f"Query result: {flat_result}"


if __name__ == "__main__":
    print(query_sql("Which customers placed an order over $500?"))
