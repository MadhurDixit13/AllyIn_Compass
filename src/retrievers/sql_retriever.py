from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_groq import ChatGroq
from sqlalchemy import create_engine
import os
import dotenv
import re
import ast

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
                                     return_direct=True,
                                    #  use_query_checker=True,  # enables basic syntax checking
                                    #  return_intermediate_steps=True
                                     )

# def preprocess_duckdb_sql(sql: str) -> str:
#     """
#     Translates MySQL-style SQL syntax (like CURDATE()) into DuckDB-compatible syntax.
#     """
#     sql = sql.replace("CURDATE()", "current_date")
#     sql = sql.replace("curdate()", "current_date")
#     sql = sql.replace("NOW()", "current_timestamp")
#     sql = sql.replace("now()", "current_timestamp")
    
#     # Fix DATE_SUB pattern
#     # MySQL: DATE_SUB(current_date, INTERVAL 7 DAY)
#     # DuckDB: current_date - INTERVAL 7 DAY
    
#     sql = re.sub(r"DATE_SUB\((current_date|current_timestamp),\s*INTERVAL\s+(\d+)\s+DAY\)", r"\1 - INTERVAL \2 DAY", sql)
#     sql = re.sub(r"DATE_SUB\((current_date|current_timestamp),\s*INTERVAL\s+(\d+)\s+MONTH\)", r"\1 - INTERVAL \2 MONTH", sql)

#     return sql


def query_sql(question: str) -> str:
    # question = preprocess_duckdb_sql(question)
    response = db_chain.invoke(question)
    result_str = response.get("result", "")

    if not result_str:
        return "No matching records found."

    try:
        # Convert the string "[('Deanna Green MD',)]" to actual list of tuples
        rows = ast.literal_eval(result_str)

        if isinstance(rows, list):
            return "\n".join(", ".join(str(item) for item in row) for row in rows)
        else:
            return str(rows)
    except Exception as e:
        return f"Failed to parse result: {e}"




if __name__ == "__main__":
    print(query_sql("Who is the customer with id 1?"))
